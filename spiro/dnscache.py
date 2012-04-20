import socket

from spiro.util.cache import LRUCache

class DNSHandler(object):
    """Cache DNS Names - this is plugged into the Tornado Async Client"""

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
