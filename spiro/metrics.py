from collections import defaultdict

class Metrics(object):
    def __init__(self):
        self._buckets = defaultdict(list)

    def __get__(self, key):
        return self._buckets[key]

    def add(self, key, value):
        self._buckets[key].append(value)

    def ave(self, key):
        def ave(l):
            return float(sum(l))/len(l) if l else 0
        return ave(self._buckets[key])
