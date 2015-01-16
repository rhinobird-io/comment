#!/usr/bin/python3

import http.client

NGINX_HOST = "localhost:9080"

def push(tid, comment):
    conn = http.client.HTTPConnection(NGINX_HOST)
    channel_path = "/pub?id=" + tid
    headers = {"Content-type": "application/json"}
    conn.request("POST", channel_path, comment, headers)
    response = conn.getresponse()
    return response.status == 200
