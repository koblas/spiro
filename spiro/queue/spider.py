from collections import defaultdict, deque
from datetime import datetime, timedelta

# This should manage seen_set

class SpiderBucket(deque):
    def __init__(self, parent=None, *args, **kwargs):
        self._processing = 0
        self._concurrent_crawler = None
        self._parent = parent

        self._delay   = None
        self._time    = datetime.now()
        self._counter = 0

        super(SpiderBucket, self).__init__(*args, **kwargs)

    def pop(self, timenow=None):
        if not self:
            return None, None

        # If the bucket is "busy"
        if timenow and self._time > timenow:
            return None, None

        if self._processing == (self._concurrent_crawler or self._parent.default_concurrency):
            return None, None

        self._time = timenow
        if self._delay:
            self._time += self._delay
        elif self._parent:
            self._time += self._parent._default_delay_td

        self._counter    += 1
        self._processing += 1

        return self.popleft(), self._callback

    def _callback(self, success, task):
        self._processing -= 1

class SpiderQueue(object):
    BUCKET_CLASS = SpiderBucket

    def __init__(self):
        self._length = 0
        self._buckets = defaultdict(lambda *a: self.BUCKET_CLASS(parent=self))
        self._last_time = None
        self._bucket_list = []
        self._bucket_idx = 0

    def __len__(self):
        return self._length

    def add(self, task):
        bucket = task.url_host
        if bucket not in self._buckets:
            self._bucket_list.append(bucket)
        self._buckets[bucket].append(task)
        self._length += 1

    def pop(self, callback):
        tnow   = datetime.now()
        retval = None, None

        for idx in range(0, len(self._bucket_list)):
            # Shift from the front to the end
            bid = self._bucket_list.pop(0)
            self._bucket_list.append(bid)
            bucket = self._buckets[bid]

            # No need to process an empty bucket
            retval = bucket.pop(timenow=tnow)
            if retval is not None:
                self._length -= 1
                break

        callback(retval)

    def __iter__(self):
        """ Primarily used as a UI query to see what's up """
        for bid, bucket in self._buckets.iteritems():
            yield bid, len(bucket), bucket._counter

    @property
    def default_concurrency(self):
        return self._default_concurrency

    @default_concurrency.setter
    def default_concurrency(self, value):
        self._default_concurrency = value

    @property
    def default_delay(self):
        return self._default_delay

    @default_delay.setter
    def default_delay(self, value):
        self._default_delay    = value
        self._default_delay_td = timedelta(seconds=value)
