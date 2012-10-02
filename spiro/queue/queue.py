from collections import deque

class SimpleQueue(object):
    def __init__(self):
        self.queue = deque()

    def pop(self):
        def callback(success):
            pass
        return self.queue.popleft(), callback

    def add(self, url):
        self.queue.append(url)

    def empty(self):
        return not bool(self.queue)
