from datetime import datetime
import logging
import pymongo

from .base import Store

class MongoStore(Store):
    def __init__(self, settings, **kwargs):
        host    = kwargs.get('store_host', settings.STORE_HOST)
        bucket = settings.STORE_BUCKET

        logging.debug("Staring Mongo connection to %s - bucket=%s" % (host, bucket))

        client = pymongo.Connection(host=host, port=getattr(settings, 'STORE_PORT', 27017) )
        self.bucket = client[bucket]['docs']
        self.bucket.create_index('url', unique=True)

    def update(self, task):
        if task.response is None:
            logging.info("Task url=%s has no response" % (task.url))
            return
        
        data = {
            'url'          : task.response.request.url,
            'domain'       : task.url_host,
            'code'         : task.response.code,
            'body'         : getattr(task, 'content', None),
            'links'        : task.links,
            'headers'      : task.response.headers,
            'content-type' : task.content_type,
            'crawl_time'   : datetime.now(),
        }

        self.bucket.insert(data)

    def has(self, url):
        data = self.bucket.find_one({'url':url})
        return bool(data)
