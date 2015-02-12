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
    def GET(self, tid, since=None):
        comments = redis_client.load_thread(tid, since)
        return comments

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
        if not comment:
            raise cherrypy.HTTPError(404)
        else:
            return json.loads(comment)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        comment = cherrypy.request.json
        comment["user"] = cherrypy.request.headers.get("X-User", None)
        if not comment["user"]:
            cherrypy.log("Cannot find 'X-User' in headers")
            raise cherrypy.HTTPError(400)

        comment["time"] = int(time.time() * 1000)
        redis_client.new_comment(comment)
        return {"cid": comment["cid"]}

    def DELETE(self, cid):
        redis_client.delete_comment(cid)


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

    cherrypy.server.socket_port = int(os.getenv("PORT", 5000))
    cherrypy.server.socket_host = "0.0.0.0"

    abspath = os.path.dirname(os.path.abspath(__file__))
    cherrypy.quickstart(Root(), "/", {
        "/elements": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": abspath + "/public/elements",
        }
    })
