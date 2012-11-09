from .base import Step
import logging
import time
from functools import partial

from tornado import ioloop
from tornado import gen
from tornado import httpclient
from spiro.models import Settings, signals
from spiro.models import PageStats
from spiro.util.cache import LRUCache

class Fetch(Step):
    default_delay = 10
    cache = LRUCache(1000)

    def __init__(self, settings, user_settings=None, **kwargs):
        self.client     = httpclient.AsyncHTTPClient()
        self.use_gzip   = settings.USE_GZIP
        self.user_agent = settings.USER_AGENT
        self.ioloop     = ioloop.IOLoop.instance()

        if user_settings:
            self.post_save(None, user_settings)

    def process(self, task, callback=None, **kwargs):
        task.request = httpclient.HTTPRequest(task.url, use_gzip=self.use_gzip, user_agent=self.user_agent)

        tnow = time.time()
        tv = self.cache.get(task.url_host)
        tnext = (tv or tnow) + self.__class__.default_delay
        if tv is not None and tnow < tnext:
            logging.debug("Fetching on timer in %.2f seconds" % (tnext - tnow))
            self.ioloop.add_timeout(tnext, partial(self.fetch, task, callback))
            return
        self.fetch(task, callback)

    @gen.engine
    def fetch(self, task, callback):
        self.cache[task.url_host] = time.time()
        task.response = yield gen.Task(self.client.fetch, task.request)

        if task.response.body:
            blen = len(task.response.body)
        else:
            blen = 0

        try:
            raw_len = int(task.response.headers.get('content-length', blen))
        except:
            raw_len = blen

        logging.debug("Fetched code=%d len_raw=%d len=%d url=%s" % (task.response.code, raw_len, blen, task.url))
        PageStats.crawled(task.response.code, raw_len)

        if task.response.code == 200:
            task.content = task.content_from_response()
        elif task.response.code in (301, 302):
            logging.error("Unhandled Redirect code=%d url=%s" % (task.response.code, task.url))
        else:
            task.content = None

        callback((Step.CONTINUE, task))

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        cls.default_delay = document.crawl_delay

signals.post_save.connect(Fetch.post_save, sender=Settings)
