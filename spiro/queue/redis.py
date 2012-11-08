import logging
from time import time
from datetime import datetime
from tornado import gen
from spiro.task import Task
from spiro.util.cache import LRUCache

from .spider import SpiderQueue, SpiderBucket

"""

Redis Data Structure:

    KEY

    Spiro:QueueURLs > LIST of hostnames that we have URLs queued for
        Redis Ops   : RPOPLPUSH Spiro:QueueURLs Spiro:QueueURLs
                    = returns the next available host to query

                    : SETNX  Spiro:QueueLock:%s INSTANCE_ID 
                      > If returns 1 - then set an expires of 60 seconds
                    : EXPIRE Spiro:QueueLock:%s TIMEOUT(60s)
                       Mark the queue item as busy

    Sprio:Queue:%s > 
        Redis Ops   
                    : ZRANGE 0 1
                       Get the element
                    : ZREM ___ URL
                       Remove the URL

"""

BUCKETS_KEY        = "Spiro:QueueURLs"
URL_QUEUE_KEY      = "Spiro:Queue:%s"
SEEN_SET           = "Spiro:SeenURLs"
QUEUE_BUCKET_LOCK  = "Spiro:QueueLock:%s"
QUEUE_LOCK_TIMEOUT = 60             # 60 seconds
QUEUE_LOCK_REFRESH = 10             # refresh the lock if we're within 10 seconds of expiration

class RedisBucket(SpiderBucket):
    def has_url(self, url):
        for task in self:
            if task.url == url:
                return True
        return False

    def _callback(self, success, task):
        super(RedisBucket, self)._callback(success, task)

        if task and success:
            self._parent.redis.sadd(SEEN_SET, task.url)
            self._parent.redis.zrem(URL_QUEUE_KEY % task.url_host, task.url)

class RedisQueue(SpiderQueue):
    BUCKET_CLASS = RedisBucket

    def __init__(self, redis):
        super(RedisQueue, self).__init__()
        self.redis = redis

        self._owned = {}
        self._seen_cache = LRUCache(10000)

        import socket, os
        self.guid  = "%s:%s" % (socket.gethostname(), os.getpid())

        self._known_buckets = set()

    @gen.engine
    def add(self, task):
        """Add a url to be queued

           Add it to the list of tracked hosts
           Add the url to the priority list of urls to be crawlled

        Thoughts:
            SEEN_SET is only added to after a URL is successfully crawled
            since once it's crawled it will be removed from the Queue 
        """

        if not task.force and task.url in self._seen_cache:
            #logging.debug("RedisQueue: SEEN %s in cache" % task.url)
            return
        self._seen_cache[task.url] = True

        if not task.force:
            (clnt, val), kw = yield gen.Task(self.redis.sismember, SEEN_SET, task.url)
            if val:
                #logging.debug("RedisQueue: SEEN %s in visited set" % task.url)
                return

        self.redis.zadd(URL_QUEUE_KEY % task.url_host, 1, task.url)

        bid = task.url_host
        if bid not in self._known_buckets:
            self._known_buckets.add(bid)
            (clnt, val), kw = yield gen.Task(self.redis.sadd, BUCKETS_KEY + "_set", bid)
            if val:
                yield gen.Task(self.redis.rpush, BUCKETS_KEY, bid)

    def __nonzero__(self):
        """ Since we have to consult Redis - we assume we've got work """
        return True

    @gen.engine
    def pop(self, callback):
        """Find an element that's available for fetching

           Strategy:  First check the internal queues/states if something is
                      ready - otherwise check redis
        """
        tval = time()
        for bid in self._bucket_list:
            # For anything that we've got work for and is close to expiration, refresh the lock
            if self._owned[bid] - tval < QUEUE_LOCK_REFRESH and self._buckets[bid]:
                self.redis.expire(QUEUE_BUCKET_LOCK % bid, QUEUE_LOCK_TIMEOUT)
                self._owned[bid] = tval + QUEUE_LOCK_TIMEOUT
                logging.debug("RedisQueue: Refreshed bucket=%s expires - pre" % bid)

        retval, cb = yield gen.Task(super(RedisQueue, self).pop)

        first_bid = None
        if not retval:
            val = False
            while not val:
                (clt, bid), kw = yield gen.Task(self.redis.rpoplpush, BUCKETS_KEY, BUCKETS_KEY)
                if bid is None or bid is "":
                    break

                #
                # Don't loop forever....
                #
                if first_bid is None:
                    first_bid = bid
                elif bid == first_bid:
                    bid = None
                    break

                #
                #  Lock the bucket - if we don't get the lock keep on going
                # 
                if bid not in self._owned or self._owned[bid] <= time():
                    (clt, val), kw = yield gen.Task(self.redis.setnx, QUEUE_BUCKET_LOCK % bid, self.guid)
                    if not val:
                        continue
                    else:
                        logging.debug("RedisQueue: Set lock on bucket=%s" % bid)
                
                # If we just aquired the lock or it's going to expire "soon" refresh the timeout
                if bid not in self._owned or self._owned[bid] - time() < QUEUE_LOCK_REFRESH:
                    yield gen.Task(self.redis.expire, QUEUE_BUCKET_LOCK % bid, QUEUE_LOCK_TIMEOUT)
                    self._owned[bid] = time() + QUEUE_LOCK_TIMEOUT
                    logging.debug("RedisQueue: Refreshed bucket=%s expires" % bid)

                # Get a batch of URLs...
                (clt, urls), kw = yield gen.Task(self.redis.zrevrange, URL_QUEUE_KEY % bid, 0, 19)

                # Queue them up
                for url in urls or []:
                    if self._buckets[bid].has_url(url):
                        continue
                    self._buckets[bid].append(Task(url))
                retval, cb = self._buckets[bid].pop(timenow=datetime.now())
                if retval:
                    break

        callback((retval, cb))

    @gen.engine
    def items(self, callback):
        """ Primarily used as a UI query to see what's up """
        (clnt, keys), kw = yield gen.Task(self.redis.lrange, BUCKETS_KEY, 0, -1)

        items = []
        for bid in keys or []:
            (clnt, cnt), kw = yield gen.Task(self.redis.zcard, URL_QUEUE_KEY % bid)
            counter = 0
            if bid in self._buckets:
                counter = self._buckets[bid]._counter
            items.append((bid, cnt, counter))
        callback(items)
