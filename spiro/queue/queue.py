from collections import deque

# TODO - Fix responses, add seen_set
class SimpleQueue(object):
    def __init__(self):
        self.queue = deque()

    def pop(self):
        def callback(success):
            pass
        return self.queue.popleft(), callback

    def add(self, task):
        self.queue.append(task)

    def empty(self):
        return not bool(self.queue)
