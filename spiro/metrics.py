from collections import defaultdict

class Metrics(object):
    def __init__(self):
        self._buckets = defaultdict(list)

    def __get__(self, key):
        """Return a specific metric"""
        return self._buckets[key]

    def add(self, key, value):
        """Add a new value to a list of metrics"""
        self._buckets[key].append(value)

    def incr(self, key, value=1):
        """Increment a metric (counter)"""
        if not self._buckets[key]:
            self._buckets[key] = [0]
        self._buckets[key][0] += value

    def value(self, key):
        def value(l):
            return l[0] if l else 0
        return value(self._buckets[key])

    def ave(self, key):
        def ave(l):
            return float(sum(l))/len(l) if l else 0
        return ave(self._buckets[key])

    def median(self, key):
        def median(l):
            return sorted(l)[len(l)/2] if l else 0
        return median(self._buckets[key])

    def items(self):
        return self._buckets.items()

systemMetrics = Metrics()
