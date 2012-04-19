from pyquery import PyQuery as pq
from urlparse import urljoin

from .base import LinkExtractorBase

class HtmlLinkExtractor(LinkExtractorBase):
    def __init__(self, settings, **kwargs):
        pass

    def process(self, response):
        url = response.request.url

        q = pq(response.body)
        for link in q('a'):
            href = link.attrib.get('href', None)
            if not href:
                continue

            full_url = urljoin(url, href)
            full_url = full_url.split('#', 1)[0]

            if full_url.startswith('http://') or full_url.startswith('https://'):
                self.add_extracted_url(response, full_url)

        return response
