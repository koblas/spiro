import logging
import urlparse
from .base import Step

"""
Instead of handling 30X redirects as a HTTP case, we're handling them in the
response pipeline.
"""

class ScheduleUrls(Step):
    def __init__(self, settings, work_queue=None, **kwargs):
        """Initialzation"""
        self.work_queue = work_queue
        self.seen_set   = set()

    def process(self, task, callback=None, **kwargs):
        for url in task.links:
            if url not in self.seen_set:
                try:
                    p = urlparse.urlparse(url)

                    self.work_queue.add(p.netloc, url)
                    self.seen_set.add(url)
                except Exception as e:
                    logging.info("Unable to add URL:", e)

        callback((Step.CONTINUE, task))
