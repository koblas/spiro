from collections import deque

class SimpleQueue(object):
    def __init__(self):
        self.queue = deque()

    def pop(self):
        return self.queue.popleft()

    def add(self, url):
        self.queue.append(url)

    def empty(self):
        return not bool(self.queue)
