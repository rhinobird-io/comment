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
    if not client.get(COUNT_THREADS_KEY):
        client.set(COUNT_THREADS_KEY, INIT_THREAD_ID)
    # Initialize counter for comments
    if not client.get(COUNT_COMMENTS_KEY):
        client.set(COUNT_COMMENTS_KEY, INIT_COMMENT_ID)


def new_thread():
    client = redis.Redis(connection_pool=POOL)
    tid = client.incr(COUNT_THREADS_KEY)
    return str(tid)


def load_thread(tid):
    client = redis.Redis(connection_pool=POOL)
    cid_list = client.lrange(tid, 0, -1)
    comment_list = []
    for cid in cid_list:
        comment = _hget_comment(client, cid)
        comment_list.append(comment)
    return comment_list


def get_comment(cid):
    client = redis.Redis(connection_pool=POOL)
    return _hget_comment(client, cid)


def new_comment(comment):
    client = redis.Redis(connection_pool=POOL)
    # Assign comment ID for new comment
    cid = client.incr(COUNT_COMMENTS_KEY)
    cid = str(cid)
    comment["cid"] = cid
    client.hset(COMMENTS_KEY, cid, json.dumps(comment))
    # Push new comment to thread queue
    tid = comment["tid"]
    client.rpush(tid, cid)
    return cid


def delete_comment(cid):
    client = redis.Redis(connection_pool=POOL)
    comment = _hget_comment(client, cid)
    tid = json.loads(comment)["tid"]
    client.lrem(tid, cid)
    client.hdel(COMMENTS_KEY, cid)
    return tid


def _hget_comment(client, cid):
    b = client.hget(COMMENTS_KEY, cid)
    return b.decode("utf-8")
