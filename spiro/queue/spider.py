from collections import defaultdict, deque
from datetime import datetime, timedelta

class SpiderBucket(deque):
    def __init__(self, parent=None, *args, **kwargs):
        self._processing = 0
        self._concurent_crawler = 1
        self._parent = parent

        self._delay   = None
        self._time    = datetime.now()
        self._counter = 0

        super(SpiderBucket, self).__init__(*args, **kwargs)

    def pop(self, timenow=None):
        if not self:
            return None

        # If the bucket is "busy"
        if timenow and self._time > timenow:
            return None

        if self._processing == self._concurent_crawler:
            return None

        self._time = timenow
        if self._delay:
            self._time += self._delay
        elif self._parent:
            self._time += self._parent._default_delay_td

        self._counter    += 1
        self._processing += 1

        return self.popleft(), self._callback

    def _callback(self, success):
        self._processing -= 1

class SpiderQueue(object):
    def __init__(self):
        self._length = 0
        self._buckets = defaultdict(lambda *a: SpiderBucket(parent=self))
        self._last_time = None
        self._bucket_list = []
        self._bucket_idx = 0

    def __len__(self):
        return self._length

    def add(self, bucket, obj):
        if bucket not in self._buckets:
            self._bucket_list.append(bucket)
        self._buckets[bucket].append(obj)
        self._length += 1

    def pop(self):
        tnow   = datetime.now()
        retval = None

        for idx in range(0, len(self._bucket_list)):
            # Shift from the front to the end
            bid = self._bucket_list.pop(0)
            self._bucket_list.append(bid)
            bucket = self._buckets[bid]

            # No need to process an empty bucket
            retval = bucket.pop(timenow=tnow)
            if retval is not None:
                self._length -= 1
                return retval

        return None

    def __iter__(self):
        for bid, bucket in self._buckets.iteritems():
            yield bid, len(bucket), bucket._counter

    @property
    def default_delay(self):
        return self._default_delay

    @default_delay.setter
    def default_delay(self, value):
        self._default_delay    = value
        self._default_delay_td = timedelta(seconds=value)
