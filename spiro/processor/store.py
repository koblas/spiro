import urlparse
from .base import LinkExtractorBase

"""
Instead of handling 30X redirects as a HTTP case, we're handling them in the
response pipeline.
"""

class StoreResponse(object):
    def __init__(self, settings):
        # TODO - import
        self.store = 1

    def process(self, response):
        self.store(response)
