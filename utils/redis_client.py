import json
import os

import redis

COUNT_THREADS_KEY = "COUNT_THREADS"
COUNT_COMMENTS_KEY = "COUNT_COMMENTS"
THREADS_KEY = "THREADS"
COMMENTS_KEY = "COMMENTS"

INIT_THREAD_ID = int(9e17)
INIT_COMMENT_ID = int(1e18)

POOL = None

# NOTE
# tid/cid returned by all following functions should be in string format.


def init_pool():
    host = os.getenv("REDIS_IP", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))

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


def new_thread(key):
    client = redis.Redis(connection_pool=POOL)
    if key:
        tid = client.hget(THREADS_KEY, key)
        if not tid:
            tid = client.incr(COUNT_THREADS_KEY)
            client.hset(THREADS_KEY, key, tid)
    else:
        tid = client.incr(COUNT_THREADS_KEY)

    return str(int(tid))


def load_thread(tid, since):
    client = redis.Redis(connection_pool=POOL)
    cids = client.lrange(tid, 0, -1)
    cids = _find_since([b.decode("utf-8") for b in cids], since)
    comments = []
    for cid in cids:
        if int(cid) < 0:
            comments.append({"cid": cid})
        else:
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
    tid = new_thread(comment["key"])
    client.rpush(tid, cid)


def delete_comment(cid):
    client = redis.Redis(connection_pool=POOL)
    comment = _hget_comment(client, cid)
    if comment:
        tid = json.loads(comment)["tid"]
        client.rpush(tid, -int(cid))
        client.hdel(COMMENTS_KEY, cid)


def _hget_comment(client, cid):
    b = client.hget(COMMENTS_KEY, cid)
    return b.decode("utf-8") if b else None


def _find_since(cids, since):
    if since and int(since) != 0:
        cids = cids[cids.index(since) + 1:]

    Map = {}
    for cid in cids:
        Map[int(cid)] = True

    result = []
    for cid in cids:
        if not Map.get(-int(cid), None):
            result.append(cid)

    return result
