#!/usr/bin/python3

import json
import os

import redis

COUNT_THREADS_KEY = "COUNT_THREADS"
COUNT_COMMENTS_KEY = "COUNT_COMMENTS"
COMMENTS_KEY = "COMMENTS"

INIT_THREAD_ID = int(9e17)
INIT_COMMENT_ID = int(1e18)

POOL = None

# NOTE
# tid/cid returned by all following functions should be in string format.


def init_pool():
    host, port = os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT")
    if not host:
        host = "localhost"
    port = int(port) if port else 6379

    global POOL
    POOL = redis.ConnectionPool(host=host, port=port, db=0, socket_timeout=5)

    try:
        client = redis.Redis(connection_pool=POOL)
        pong = client.ping()
        return pong, "%s:%d" % (host, port)
    except redis.exceptions.ConnectionError as e:
        return False, str(e)


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


def load_thread(tid, since):
    client = redis.Redis(connection_pool=POOL)
    cids = client.lrange(tid, 0, -1)
    since = int(since) if since else -1
    comments = []
    for cid in cids:
        if int(cid) > since:
            comment = _hget_comment(client, cid)
            comments.append(json.loads(comment))
    return comments


def get_comment(cid):
    client = redis.Redis(connection_pool=POOL)
    return _hget_comment(client, cid)


def new_comment(comment):
    client = redis.Redis(connection_pool=POOL)
    # Assign comment ID to new comment
    cid = str(client.incr(COUNT_COMMENTS_KEY))
    comment["cid"] = cid
    client.hset(COMMENTS_KEY, cid, json.dumps(comment))
    # Push new comment to thread queue
    client.rpush(comment["tid"], cid)


def delete_comment(cid):
    client = redis.Redis(connection_pool=POOL)
    comment = _hget_comment(client, cid)
    if comment:
        tid = json.loads(comment)["tid"]
        client.lrem(tid, cid)
        client.hdel(COMMENTS_KEY, cid)


def _hget_comment(client, cid):
    b = client.hget(COMMENTS_KEY, cid)
    return b.decode("utf-8") if b else None
