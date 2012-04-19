from datetime import timedelta
import tornado.ioloop
from tornado import gen
from tornado import httpclient
from spiro.util.cache import LRUCache
import socket

from .queue import Queue

class DNSHandler(object):
    """Cache DNS Names"""

    def __init__(self):
        self.cache = LRUCache(1000)
    
    def get(self, host, default=None):
        """Mimic Dictionary get's but handling them through a cache"""

        addr = self.cache.get(host, None)
        if addr:
            return addr

        addrinfo = socket.getaddrinfo(host, 80, 0, 0, socket.SOL_TCP)
        af, socktype, proto, canonname, sockaddr = addrinfo[0]

        self.cache[host] = sockaddr[0]
        return sockaddr[0]
    
class Fetcher(object):
    """Fetch documents"""

    QUEUE = Queue()

    def __init__(self, queue=None, process=None, io_loop=None):
        self.client  = httpclient.AsyncHTTPClient(hostname_mapping=DNSHandler())
        self.process = process
        self.ioloop  = io_loop or tornado.ioloop.IOLoop.instance()
        if queue:
            self.queue = queue
        else:
            self.queue = self.QUEUE

        self.ioloop.add_timeout(timedelta(seconds=1), self.loop)

    @gen.engine
    def loop(self):
        if not self.queue.empty():
            url = self.queue.pop()

            print "GOT ",url

            # TODO - fetch robots.txt

            response = yield gen.Task(self.client.fetch, url)

            if self.process:
                self.process(response)

        self.ioloop.add_timeout(timedelta(seconds=1), self.loop)

if __name__ == '__main__':
    import sys
    count = 0

    def success(url, response):
        global count
        print "Status = %d   url = %s" % (response.code, url)
        count -= 1
        if count == 0:
            tornado.ioloop.IOLoop.instance().stop()

    urls = sys.argv[1:]
    count = len(urls)

    fetcher = Fetcher(urls, success)
    tornado.ioloop.IOLoop.instance().start()
