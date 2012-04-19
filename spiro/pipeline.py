from tornado.util import import_object

class Pipeline(object):
    def __init__(self, stages=[], **kwargs):
        self.steps = []
        for item in stages:
            if type(item) == type(''):
                cls = import_object(item)
            else:
                cls = item
            self.steps.append(cls(**kwargs))

    def __call__(self, *args, **kwargs):
        for item in self.steps:
            v = item.process(*args, **kwargs)
