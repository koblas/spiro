from pyquery import PyQuery as pq
from urlparse import urljoin

from .base import Step

class HtmlLinkExtractor(Step):
    def __init__(self, settings, **kwargs):
        self.enable_nofollow = True

    def process(self, task, callback=None, **kwargs):
        if task.response.body:
            url = task.request.url

            q = pq(task.response.body.replace(' xmlns="', ' xmlnamespace="'))

            if self.enable_nofollow:
                for meta in q('meta'):
                    if meta.attrib.get('name', "").lower() != 'robots':
                        continue
                    content = meta.attrib.get('content', None)
                    if not content:
                        continue

                    if 'nofollow' in content.lower().split(','):
                        return callback((Step.CONTINUE, task))

            for link in q('a'):
                rel  = link.attrib.get('rel', '')
                href = link.attrib.get('href', None)
                if not href or (self.enable_nofollow and rel.lower() == 'nofollow'):
                    continue

                full_url = urljoin(url, href)
                full_url = full_url.split('#', 1)[0]

                if full_url.startswith('http://') or full_url.startswith('https://'):
                    task.links.append(full_url)

        callback((Step.CONTINUE, task))
