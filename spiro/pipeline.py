import logging
import time
from tornado import gen
from tornado.util import import_object
from spiro.processor.base import Step
from spiro.metrics import systemMetrics

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
            logging.debug("Running %s %r", item.name, args[0])

            try:
                t0 = time.time()
                yvalue = yield gen.Task(item.process, *nargs, **kwargs)
                dt = time.time() - t0

                systemMetrics.add('pipeline:%s:time' % item.name, dt)
                systemMetrics.incr('pipeline:%s:calls' % item.name)
            except Exception as e:
                logging.error("Pipeline Exception", e)

            action, res = yvalue

            if action == Step.STOP:
                logging.debug("Processing stoped by %s" % item.__class__.__name__)
                break
            nargs = [res]

        if callback:
            callback(res)
