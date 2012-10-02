import urlparse
from .base import Step

"""
Instead of handling 30X redirects as a HTTP case, we're handling them in the
response pipeline.
"""

class RedirectExtraction(Step):
    def __init__(self, settings, **kwargs):
        """Initialzation"""
        pass

    def process(self, task, callback=None, **kwargs):
        if 300 <= task.response.code < 400:
            location = task.response.headers.get('location', None)
            
            if not location:
                callback((Step.CONTINUE, task))

            if location.find('://') == -1:
                location = urlparse.urljoin(task.request.url, location)

            task.links.append(location)

        callback((Step.CONTINUE, task))
