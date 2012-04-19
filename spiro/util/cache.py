"""
a simple LRU (Least-Recently-Used) cache module

This module provides very simple LRU (Least-Recently-Used) cache
functionality.

An *LRU cache*, on the other hand, only keeps _some_ of the results in
memory, which keeps you from overusing resources. The cache is bounded
by a maximum size; if you try to add more values to the cache, it will
automatically discard the values that you haven't read or written to
in the longest time. In other words, the least-recently-used items are
discarded. [1]_

.. [1]: 'Discarded' here means 'removed from the cache'.

"""

from collections import deque
from time import time

__version__   = "0.1"
__all__       = ['CacheKeyError', 'LRUCache']
__docformat__ = 'reStructuredText en'


class CacheKeyError(KeyError):
    """Error raised when cache requests fail
    
    When a cache record is accessed which no longer exists (or never did),
    this error is raised. To avoid it, you may want to check for the existence
    of a cache record before reading or deleting it."""
    pass

class LRUCache(object):
    """Least-Recently-Used (LRU) cache.
    
    Instances of this class provide a least-recently-used (LRU) cache. They
    emulate a Python mapping type. You can use an LRU cache more or less like
    a Python dictionary, with the exception that objects you put into the
    cache may be discarded before you take them out.
    
    Some example usage::
	
    cache = LRUCache(32) # new cache
    cache['foo'] = get_file_contents('foo') # or whatever
	
    if 'foo' in cache: # if it's still in cache...
	    # use cached version
        contents = cache['foo']
    else:
	    # recalculate
        contents = get_file_contents('foo')
	    # store in cache for next time
        cache['foo'] = contents

    print cache.size # Maximum size
	
    print len(cache) # 0 <= len(cache) <= cache.size
	
    cache.size = 10 # Auto-shrink on size assignment
	
    for i in range(50): # note: larger than cache size
        cache[i] = i
	    
    if 0 not in cache: print 'Zero was discarded.'

    if 42 in cache:
        del cache[42] # Manual deletion

    for j in cache:   # iterate (in LRU order)
        print j, cache[j] # iterator produces keys, not values

    >>> c = LRUCache()
    >>> c
    <LRUCache: (0 elements)>
    >>> c['test'] = 1
    >>> c
    <LRUCache: (1 elements)>
    """
    DEFAULT_SIZE = 16
    """Default size of a new LRUCache object, if no 'size' argument is given."""
    
    def __init__(self, size=DEFAULT_SIZE, *args, **kw):
        """
        Maximum size of the cache.  If more than 'size' elements are added to the cache,
        the least-recently-used ones will be discarded.

        >>> LRUCache(50, {'a':1,'b':2})
        <LRUCache: (2 elements)>
        >>> LRUCache(3, {'a':1,'b':2,'d':3,'e':4})
        <LRUCache: (3 elements)>
        """
        # Check arguments

        self.__dict = dict(*args, **kw)
        self.__heap = deque(self.__dict.iterkeys())
        self._count = len(self.__dict)
        self._set_size(size)

    def __len__(self):
        """
        >>> c = LRUCache()
        >>> c['test'] = 1
        >>> c['foo'] = 2
        >>> c['bar'] = 3
        >>> c['test'] = 9
        >>> del c['bar']
        >>> len(c)
        2
        """
        return self._count
    
    def __contains__(self, key):
        """
        >>> c = LRUCache()
        >>> c['test'] = 1
        >>> c['foo'] = 2
        >>> c['bar'] = 3
        >>> c['test'] = 9
        >>> 'bar' in c
        True
        >>> 'xxx' in c
        False
        """
        return key in self.__dict

    def _set_size(self, size) :
        """
        >>> c = LRUCache(10)
        >>> for v in range(0, 20) : c[v] = 100+v
        >>> [i for i in c ]
        [19, 18, 17, 16, 15, 14, 13, 12, 11, 10]
        >>> len(c)
        10
        >>> c.size = 5
        >>> len(c)
        5
        """

        if size <= 0 :
            raise ValueError, size

        self._size = size
        while len(self.__heap) > self._size :
            del self.__dict[self.__heap.pop()]
        self._count = len(self.__heap)

    def _get_size(self) :
        """
        >>> c = LRUCache(10)
        >>> c.size
        10
        """
        return self._size

    size = property(_get_size, _set_size)
    
    def __setitem__(self, key, obj) :
        """
        >>> c = LRUCache({'foo': 2})
        >>> c['foo'] = 8
        >>> c['foo']
        8
        """
        if self.__dict.has_key(key) :
            self.__dict[key] = obj
            self.__heap.remove(key)
        else :
            self.__dict[key] = obj
            self._count += 1
            if self._count > self._size :
                del self.__dict[self.__heap.pop()]
                self._count -= 1
        self.__heap.appendleft(key)
	
    def __getitem__(self, key) :
        """
        >>> c = LRUCache({'foo': 2})
        >>> c['foo']
        2
        >>> c['bar']
        Traceback (most recent call last):
            ...
        CacheKeyError: 'bar'
        """
        if not self.__dict.has_key(key):
            raise CacheKeyError(key)

        obj = self.__dict[key]
        self.__heap.remove(key)
        self.__heap.appendleft(key)
        return obj

    def get(self, key, dval=None) :
        """
        >>> c = LRUCache()
        >>> c['foo'] = 2
        >>> c.get('foo')
        2
        >>> c.get('bar', 3)
        3
        """
        if not self.__dict.has_key(key):
            return dval
        
        obj = self.__dict[key]
        self.__heap.remove(key)
        self.__heap.appendleft(key)
        return obj
	
    def __delitem__(self, key) :
        """
        >>> c = LRUCache()
        >>> c['test'] = 1
        >>> c['foo'] = 2
        >>> c['bar'] = 3
        >>> c['test'] = 9
        >>> c['test'] = 1
        >>> del c['bar']
        >>> [i for i in c ]
        ['test', 'foo']
        """
        if not self.__dict.has_key(key):
            raise CacheKeyError(key)

        self._count -= 1
        obj = self.__dict[key]
        del self.__dict[key]
        self.__heap.remove(key)
        return obj

    def __iter__(self) :
        """
        >>> c = LRUCache()
        >>> c['test'] = 1
        >>> c['foo'] = 2
        >>> c['bar'] = 3
        >>> c['test'] = 9
        >>> [i for i in c ]
        ['test', 'bar', 'foo']
        """
        return self.__heap.__iter__()

    def __repr__(self):
        """
        >>> LRUCache()
        <LRUCache: (0 elements)>
        """
        return "<%s: (%d elements)>" % (self.__class__.__name__, len(self.__heap))

class TimedLRUCache(object) :
    """Least-Recently-Used (LRU) cache, with object expiration.
    
    Instances of this class provide a least-recently-used (LRU) cache. They
    emulate a Python mapping type. You can use an LRU cache more or less like
    a Python dictionary, with the exception that objects you put into the
    cache may be discarded before you take them out.
    
    Some example usage::
	
    cache = TimedLRUCache(32) # new cache
    cache['foo'] = get_file_contents('foo') # or whatever
	
    if 'foo' in cache: # if it's still in cache...
	    # use cached version
        contents = cache['foo']
    else:
	    # recalculate
        contents = get_file_contents('foo')
	    # store in cache for next time
        cache['foo'] = contents

    print cache.size # Maximum size
	
    print len(cache) # 0 <= len(cache) <= cache.size
	
    cache.size = 10 # Auto-shrink on size assignment
	
    for i in range(50): # note: larger than cache size
        cache[i] = i
	    
    if 0 not in cache: print 'Zero was discarded.'

    if 42 in cache:
        del cache[42] # Manual deletion

    for j in cache:   # iterate (in LRU order)
        print j, cache[j] # iterator produces keys, not values

    >>> c = TimedLRUCache()
    >>> c
    <TimedLRUCache: (0 elements)>
    >>> c['test'] = 1
    >>> c
    <TimedLRUCache: (1 elements)>
    """
    DEFAULT_SIZE = 16
    """Default size of a new TimedLRUCache object, if no 'size' argument is given."""
    
    def __init__(self, size=DEFAULT_SIZE, expires=None):
        """
        Maximum size of the cache.  If more than 'size' elements are added to the cache,
        the least-recently-used ones will be discarded.
        """
        # Check arguments
        if size <= 0 :
            raise ValueError, size
        self.__heap = deque()
        self.__dict = {}
        self._size  = size
        self._count = 0
        self._default_expires = expires

    def __len__(self):
        return self._count
    
    def __contains__(self, key):
        """
        >>> c = TimedLRUCache()
        >>> c['test'] = 1
        >>> c['foo'] = 2
        >>> c['bar'] = 3
        >>> c['test'] = 9
        >>> 'bar' in c
        True
        >>> 'xxx' in c
        False
        """
        return key in self.__dict

    def _set_size(self, size) :
        """
        >>> c = TimedLRUCache(10)
        >>> for v in range(0, 20) : c[v] = 100+v
        >>> [i for i in c ]
        [19, 18, 17, 16, 15, 14, 13, 12, 11, 10]
        >>> len(c)
        10
        >>> c.size = 5
        >>> len(c)
        5
        """
        self._size = size
        while len(self.__heap) > self._size :
            del self.__dict[self.__heap.pop()]
        self._count = len(self.__heap)

    def _get_size(self) :
        return self._size

    size = property(_get_size, _set_size)

    def _build_expires(self) :
        if not self._default_expires :
            return None
        return time() + self._default_expires
    
    def __setitem__(self, key, obj) :
        self.put(key, obj, None)

    def put(self, key, obj, exp = None) :
        exp = exp or self._build_expires()
        if self.__dict.has_key(key) :
            self.__dict[key] = (exp, obj)
            self.__heap.remove(key)
        else :
            self.__dict[key] = (exp, obj)
            self._count += 1
            if self._count > self._size :
                del self.__dict[self.__heap.pop()]
                self._count -= 1
        self.__heap.appendleft(key)
	
    def __getitem__(self, key) :
        if not self.__dict.has_key(key):
            raise CacheKeyError(key)

        obj = self.__dict[key]
        self.__heap.remove(key)
        self.__heap.appendleft(key)
        ts = obj[0]
        if ts and ts < time() :
            del self[key]
            return None
        return obj[1]

    def get(self, key, dval=None) :
        if not self.__dict.has_key(key):
            return dval
        
        obj = self.__dict[key]
        self.__heap.remove(key)
        self.__heap.appendleft(key)
        ts = obj[0]
        if ts and ts < time() :
            del self[key]
            return None
        return obj[1]
	
    def __delitem__(self, key) :
        """
        >>> c = TimedLRUCache()
        >>> c['test'] = 1
        >>> c['foo'] = 2
        >>> c['bar'] = 3
        >>> c['test'] = 9
        >>> c['test'] = 1
        >>> del c['bar']
        >>> [i for i in c ]
        ['test', 'foo']
        """
        if not self.__dict.has_key(key):
            raise CacheKeyError(key)

        self._count -= 1
        obj = self.__dict[key]
        del self.__dict[key]
        self.__heap.remove(key)
        return obj[1]

    def __iter__(self) :
        """
        >>> c = TimedLRUCache()
        >>> c['test'] = 1
        >>> c['foo'] = 2
        >>> c['bar'] = 3
        >>> c['test'] = 9
        >>> [i for i in c ]
        ['test', 'bar', 'foo']
        """
        return self.__heap.__iter__()

    def __repr__(self):
        return "<%s: (%d elements)>" % (self.__class__.__name__, len(self.__heap))

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    from time import time
    s_time = time()
    c = LRUCache(10000)
    for i in range(0, c.size * 100) :
        c[i] = 7
    e_time = time()

    print "Total time = %5.2f" % (e_time - s_time)
