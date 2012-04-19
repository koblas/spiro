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

    def update(self, response):
        data = {
            'url'          : response.request.url,
            'code'         : response.code,
            'body'         : response.body,
            'headers'      : response.headers,
            'content-type' : response.headers.get('content-type'),
            'crawl_time'   : datetime.now(),
        }

        self.bucket.new(response.request.url, data).store()
