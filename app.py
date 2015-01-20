#!/usr/bin/python3

import json
import time
import cherrypy

import utils.nginx_client as nginx_client
import utils.redis_client as redis_client

from utils.nginx_client import NGINX_HOST

WS_URL = "ws://" + NGINX_HOST + "/ws/%s?time=Thu, 01 Jan 2015 00:00:00"


class Thread(object):
    exposed = True

    def _cp_dispatch(self, vpath):
        if len(vpath) == 2:
            cherrypy.request.params["tid"] = vpath.pop(0)
            return self

    @cherrypy.tools.json_out()
    def GET(self, tid):
        # Load a thread from Redis to Nginx
        if nginx_client.is_open(tid) == False:
            comment_list = redis_client.load_thread(tid)
            # The result of last is_open() might expire
            if nginx_client.is_open(tid) == False:
                for comment in comment_list:
                    nginx_client.push(tid, comment)
        return {"url": WS_URL % tid}

    @cherrypy.tools.json_out()
    def POST(self):
        tid = redis_client.new_thread()
        return {"tid": tid}


class Comment(object):
    exposed = True

    def _cp_dispatch(self, vpath):
        if len(vpath) == 2:
            cherrypy.request.params["cid"] = vpath.pop(0)
            return self

    @cherrypy.tools.json_out()
    def GET(self, cid):
        comment = redis_client.get_comment(cid)
        return json.loads(comment)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        comment = cherrypy.request.json
        comment["time"] = int(time.time())
        cid = redis_client.new_comment(comment)
        tid = comment["tid"]
        if nginx_client.is_open(tid):
            nginx_client.push(comment["tid"], json.dumps(comment))
        return {"cid": str(cid)}

    def DELETE(self, cid):
        tid = redis_client.delete_comment(cid)
        if nginx_client.is_open(tid):
            false_comment = json.dumps({
                "tid": tid,
                "cid": cid,
                "body": None,
            })
            nginx_client.push(tid, false_comment)
        return ""
        

def start():
    cherrypy.log("\bConnecting to Redis...")
    redis_client.init_pool()  # TODO test connection
    redis_client.init_count()

def stop():
    cherrypy.log("\bShutting down Redis...")
    redis_client.POOL.disconnect()

if __name__ == "__main__":
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": False,
        }
    }
    cherrypy.tree.mount(Thread(), "/thread", conf)
    cherrypy.tree.mount(Comment(), "/comment", conf)

    cherrypy.engine.subscribe("start", start)
    cherrypy.engine.subscribe("stop", stop)

    cherrypy.engine.start()
    cherrypy.engine.block()
