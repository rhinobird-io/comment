#!/usr/bin/python3

import json
import redis

COUNT_THREADS_KEY = "COUNT_THREADS"
COUNT_COMMENTS_KEY = "COUNT_COMMENTS"
COMMENTS_KEY = "COMMENTS"

INIT_THREAD_ID = int(9e17)
INIT_COMMENT_ID = int(1e18)

POOL = None

def init_pool():
    global POOL
    POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

def init_count():
    client = redis.Redis(connection_pool=POOL)
    # Initialize counter for threads
    if client.get(COUNT_THREADS_KEY) == None:
        client.set(COUNT_THREADS_KEY, INIT_THREAD_ID)
    # Initialize counter for comments
    if client.get(COUNT_COMMENTS_KEY) == None:
        client.set(COUNT_COMMENTS_KEY, INIT_COMMENT_ID)

def new_thread():
    client = redis.Redis(connection_pool=POOL)
    tid = client.incr(COUNT_THREADS_KEY)
    return tid

def new_comment(comment):
    client = redis.Redis(connection_pool=POOL)
    # Assign comment ID for new comment
    cid = client.incr(COUNT_COMMENTS_KEY)
    comment["id"] = str(cid)
    client.hset(COMMENTS_KEY, cid, json.dumps(comment))
    # Push new comment to thread queue
    tid = comment["tid"]
    client.rpush(tid, cid)
    return cid

def delete_comment(tid, cid):
    client = redis.Redis(connection_pool=POOL)
    client.lrem(tid, cid)
