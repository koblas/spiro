import logging
from tornado import gen
from spiro.task import Task
from .base import Step
from .fetch import Fetch
from .store import StoreResponse
from spiro.util.robotparser import RobotParser
from spiro.util.cache import LRUCache
from spiro.models import RobotRule, signals

"""
Process a robots.txt file - and actually use it to control what's fetched
"""

class RobotCheck(Step):
    cache = LRUCache(1000)

    @classmethod
    def post_save_clear(cls, sender, document, **kwargs):
        logging.debug("Removing robots.txt cache information for: %s" % document.site)

        for scheme in ('http', 'https'):
            url = "%s://%s/robots.txt" % (scheme, document.site)
            if url in cls.cache:
                del cls.cache[url]

    def __init__(self, settings, **kwargs):
        """Initialzation"""
        self.settings = settings
        self.fetch    = Fetch(settings)
        self.store    = StoreResponse(settings)

    @gen.engine
    def process(self, task, callback=None, **kwargs):
        url = "%s://%s/robots.txt" % (task.url_scheme, task.url_host)

        if url in self.cache:
            matcher = self.cache[url]
        else:
            matcher = self.cache[url] = yield gen.Task(self.build_matcher, url)
            # TODO - Get Crawl Delay ``matcher.get_crawl_delay()``
            
        if matcher.is_allowed_path(task.url_path):
            callback((Step.CONTINUE, task))
            return

        callback((Step.STOP, task))

    @gen.engine
    def build_matcher(self, url, callback):
        task   = Task(url)
        extra_rules = []

        for rule in RobotRule.objects(site=task.url_host):
            extra_rules.append(('allow' if rule.flag else 'deny', rule.path))

        parser = RobotParser(useragent=self.settings.USER_AGENT, extra_rules=extra_rules)

        v, t = yield gen.Task(self.fetch.process, task)

        # Save the robots.txt
        yield gen.Task(self.store.process, task)

        if task.content:
            parser.parse(task.content)

        matcher = parser.matcher(self.settings.ROBOT_NAME)

        callback(matcher)

signals.post_save.connect(RobotCheck.post_save_clear, sender=RobotRule)
signals.pre_delete.connect(RobotCheck.post_save_clear, sender=RobotRule)
