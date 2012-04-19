from datetime import datetime
import logging
import pymongo

from .base import Store

class RiakStore(Store):
    def __init__(self, settings, **kwargs):
        host    = kwargs.get('store_host', settings.STORE_HOST)
        bucket = settings.STORE_BUCKET

        logging.debug("Staring Mongo connection to %s - bucket=%s" % (host, bucket))

        client = pymongo.Connection(host=host)
        self.bucket = client[bucket]

        self.bucket.create_index('url', unique=True)

    def update(self, response):
        data = {
            'url'          : response.request.url,
            'code'         : response.code,
            'body'         : response.body,
            'headers'      : response.headers,
            'content-type' : response.headers.get('content-type'),
            'crawl_time'   : datetime.now(),
        }

        self.bucket.insert(data)
