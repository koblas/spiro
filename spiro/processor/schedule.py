import logging
import urlparse
from spiro.task import Task
from .base import Step

"""
Instead of handling 30X redirects as a HTTP case, we're handling them in the
response pipeline.
"""

class ScheduleUrls(Step):
    def __init__(self, settings, work_queue=None, user_settings=None, **kwargs):
        """Initialzation"""
        self.restrict      = getattr(settings, 'DOMAIN_RESTRICT', None)
        self.work_queue    = work_queue
        self.settings      = settings
        self.user_settings = user_settings
        self.seen_set = set()

    def process(self, task, callback=None, **kwargs):
        # Link following turned off...

        if not self.user_settings.follow_links:
            callback((Step.CONTINUE, task))
            return

        for url in task.links:
            if url not in self.seen_set:
                try:
                    p = urlparse.urlparse(url)

                    try:
                        host = p.netloc
                        host, port = host.split(':')
                    except:
                        pass

                    #
                    #  In INTERNET mode only restrict if there is a restriction set in place, otherwise 
                    #  you can crawl whatever.
                    #
                    if self.settings.INTERNET:
                        if self.user_settings.domain_restriction and host not in self.user_settings.domain_restriction:
                            continue
                    elif host not in self.user_settings.domain_restriction:
                        continue

                    self.work_queue.add(Task(url))
                except Exception as e:
                    logging.info("Unable to add URL:", e)

        callback((Step.CONTINUE, task))
