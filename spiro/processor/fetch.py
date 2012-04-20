from .base import Step
from tornado import gen
from tornado import httpclient

from spiro.dnscache import DNSHandler

class Fetch(Step):
    def __init__(self, settings, **kwargs):
        self.client     = httpclient.AsyncHTTPClient(hostname_mapping=DNSHandler())
        self.use_gzip   = settings.USE_GZIP
        self.user_agent = settings.USER_AGENT

    @gen.engine
    def process(self, task, callback=None, **kwargs):
        task.request = httpclient.HTTPRequest(task.url, use_gzip=self.use_gzip, user_agent=self.user_agent)
        task.response = yield gen.Task(self.client.fetch, task.request)

        task.content = task.content_from_response()

        callback((Step.CONTINUE, task))
