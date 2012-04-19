import urlparse
from .base import LinkExtractorBase

"""
Instead of handling 30X redirects as a HTTP case, we're handling them in the
response pipeline.
"""

class ScheduleUrls(LinkExtractorBase):
    def __init__(self, settings, work_queue=None, **kwargs):
        """Initialzation"""
        self.work_queue = work_queue

    def process(self, response, **kwargs):
        if self.work_queue and hasattr(response, 'spiro_extracted_urls'):
            for url in response.spiro_extracted_urls:
                self.work_queue.add(url)

        return response
