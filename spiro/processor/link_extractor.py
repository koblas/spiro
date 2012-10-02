from pyquery import PyQuery as pq
from urlparse import urljoin

from .base import Step

class HtmlLinkExtractor(Step):
    def __init__(self, settings, **kwargs):
        pass

    def process(self, task, callback=None, **kwargs):
        if task.response.body:
            url = task.request.url

            q = pq(task.response.body)
            for link in q('a'):
                href = link.attrib.get('href', None)
                if not href:
                    continue

                full_url = urljoin(url, href)
                full_url = full_url.split('#', 1)[0]

                if full_url.startswith('http://') or full_url.startswith('https://'):
                    task.links.append(full_url)

        callback((Step.CONTINUE, task))
