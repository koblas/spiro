from datetime import datetime
import logging
import riak

from .base import Store

class RiakStore(Store):
    def __init__(self, settings, **kwargs):
        host    = kwargs.get('store_host', settings.STORE_HOST)
        bucket = settings.STORE_BUCKET

        logging.debug("Staring Riak connection to %s - bucket=%s" % (host, bucket))

        #client = riak.RiakClient(host=host, port=settings.RIAK_PROTOCOL_BUFFERS_PORT, transport_class=riak.RiakPbcTransport)
        client = riak.RiakClient(host=host, transport_class=riak.RiakPbcTransport)
        self.bucket = client.bucket(bucket)

    def update(self, task):
        if task.response is None:
            logging.info("Task url=%s has no response" % (task.url))
            return

        data = {
            'url'          : task.response.request.url,
            'code'         : task.response.code,
            'body'         : getattr(task, 'content', None),
            'links'        : task.links,
            'headers'      : task.response.headers,
            'content-type' : task.content_type,
            'crawl_time'   : datetime.now(),
        }

        self.bucket.new(task.response.request.url, data).store()

    def has(self, url):
        # TODO - implement has()
        return True
