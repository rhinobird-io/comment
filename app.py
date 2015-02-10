#!/usr/bin/python3

import json
import os
import time

import cherrypy

import utils.redis_client as redis_client


class Thread(object):
    exposed = True

    def _cp_dispatch(self, vpath):
        if len(vpath) == 2:
            cherrypy.request.params["tid"] = vpath.pop(0)
            return self

    @cherrypy.tools.json_out()
    def GET(self, tid):
        # Load a thread from Redis to Nginx
        if not nginx_client.is_open(tid):
            comment_list = redis_client.load_thread(tid)
            # The result of last is_open() might expire
            if not nginx_client.is_open(tid):
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


class Root():
    pass


def start():
    cherrypy.log("\bConnecting to Redis...")
    ok, msg = redis_client.init_pool()
    if ok:
        cherrypy.log("\bConnected to Redis [%s]" % msg)
        redis_client.init_count()
    else:
        cherrypy.log(msg)
        cherrypy.engine.exit()


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

    abspath = os.path.dirname(os.path.abspath(__file__))
    cherrypy.quickstart(Root(), "/", {
        "/public": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": abspath + "/public",
        }
    })
