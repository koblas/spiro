from .base import Step
import logging
from tornado import gen
from tornado import httpclient

from spiro.dnscache import DNSHandler

class Fetch(Step):
    def __init__(self, settings, **kwargs):
        #self.client     = httpclient.AsyncHTTPClient(hostname_mapping=DNSHandler())
        self.client     = httpclient.AsyncHTTPClient()
        self.use_gzip   = settings.USE_GZIP
        self.user_agent = settings.USER_AGENT

    @gen.engine
    def process(self, task, callback=None, **kwargs):
        task.request = httpclient.HTTPRequest(task.url, use_gzip=self.use_gzip, user_agent=self.user_agent)
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

        if task.response.code == 200:
            task.content = task.content_from_response()
        elif task.response.code in (301, 302):
            logging.error("Unhandled Redirect code=%d url=%s" % (task.response.code, task.url))
        else:
            task.content = None

        callback((Step.CONTINUE, task))
