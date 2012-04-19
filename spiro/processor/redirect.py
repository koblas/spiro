import urlparse
from .base import LinkExtractorBase

"""
Instead of handling 30X redirects as a HTTP case, we're handling them in the
response pipeline.
"""

class RedirectExtraction(LinkExtractorBase):
    def __init__(self, settings, **kwargs):
        """Initialzation"""
        pass

    def process(self, response, **kwargs):
        if 300 <= response.code < 400:
            location = response.headers.get('location', None)
            
            if not location:
                return response

            if location.find('://') == -1:
                location = urlparse.urljoin(response.request.url, location)

            self.add_extracted_url(response, location)

        return response
