from tornado import gen
from tornado.util import import_object
from spiro.processor.base import Step

class Pipeline(object):
    def __init__(self, stages=[], **kwargs):
        self.steps = []
        for item in stages:
            if type(item) == type(''):
                cls = import_object(item)
            else:
                cls = item
            self.steps.append(cls(**kwargs))

    @gen.engine
    def process(self, *args, **kwargs):
        if not args:
            args = [None]

        callback = kwargs.pop('callback')

        nargs = args
        for item in self.steps:
            yvalue = yield gen.Task(item.process, *nargs, **kwargs)

            # print "Call = %r   Val = %r" % (item, yvalue)
            action, res = yvalue

            if action == Step.STOP:
                break
            # print 'in = %r   out = %r' % (nargs[0], res)
            nargs = [res]

        if callback:
            callback(res)
