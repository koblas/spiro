import logging
from collections import defaultdict
from blinker import Signal
from spiro.signal import client_message
#from spiro.models import signals

import tornadio2
from tornadio2 import gen
import json
from sockjs.tornado import SockJSRouter, SockJSConnection

#
#
#
class BacksyncChannel(SockJSConnection):
    master_session = None
    listeners = set()
    _events = defaultdict(list)

    def on_open(self, request):
        #
        #  We've got self.session and request to work with
        #
        self.listeners.add(self)

        self.__class__.master_session = self

        def wrap(func):
            def inner(*args, **kwargs) :
                return None, func(*args, **kwargs)
            return inner

        # TEST

    def on_close(self):
        for handler in self._events['close']:
            handler(self.session)
        self.listeners.remove(self)

    def on_message(self, message):
        try:
            msg = json.loads(message)
        except :
            pass

        model, method = msg['event'].split(':', 1)

        cls = self.instance(model)
        obj = cls(self.session)

        data  = msg.get('data', None)
        txid  = msg.get('id', None)

        logging.debug("[%s] EVENT = %s:%s  DATA = %r" % (txid, model, method, data))

        func = getattr(obj, method)
        result = None

        if func:
            if data is None:
                result = func()
            else:
                result = func(**data)
        else:
            logging.info("Missing method on %s for %s" % (model, method))

        if txid:
            response = {
                'id'    : txid,
                'event' : '%s:%s' %  (model, method),
                'data'  : result
            }
            self.send(response)

    @classmethod
    def notify(cls, event, data):
        message = {'event': event, 'data' : data}
        if cls.master_session:
            cls.master_session.broadcast(cls.listeners, message)

#BacksyncRouter = SockJSRouter(BacksyncChannel, '/backsync')
BacksyncRouter = SockJSRouter(BacksyncChannel, '/backsync')
