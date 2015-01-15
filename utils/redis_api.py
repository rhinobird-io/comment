#!/usr/bin/python3

import json
import redis

COUNT_THREADS_KEY = "COUNT_THREADS"
COUNT_COMMENTS_KEY = "COUNT_COMMENTS"
COMMENTS_KEY = "COMMENTS"

POOL = None

def init_pool():
    POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

def init_count():
    client = redis.Redis(connection_pool=POOL)
    if client.get(COUNT_THREADS_KEY) == None:
        client.set(COUNT_THREADS_KEY, int(9e17))
    if client.get(COUNT_COMMENTS_KEY) == None:
        client.set(COUNT_COMMENTS_KEY, int(1e18))

def new_thread():
    client = redis.Redis(connection_pool=POOL)
    tid = client.incr(COUNT_THREADS_KEY)
    return tid

def new_comment(comment):
    client = redis.Redis(connection_pool=POOL)
    cid = client.incr(COUNT_COMMENTS_KEY)
    comment["id"] = str(cid)
    client.hset(COMMENTS_KEY, cid, json.dumps(comment))
    return cid

