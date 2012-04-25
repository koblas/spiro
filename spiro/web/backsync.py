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
    MODELS = []
    _events = defaultdict(list)

    @classmethod
    def register(cls, name, model):
        cls.MODELS.append((name, model))

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

        for name, model in self.MODELS:
            for method in ['read', 'upsert', 'delete']:
                m = getattr(model, 'handle_%s' % method, None)
                if m:
                    self._events["%s:%s" % (name, method)].append(wrap(m))
            for method in ['open', 'close']:
                m = getattr(model, 'handle_%s' % method, None)
                if m:
                    self._events["%s" % (method)].append(m)

        for handler in self._events['open']:
            handler(self.session)

    def on_close(self):
        for handler in self._events['close']:
            handler(self.session)
        self.listeners.remove(self)

    def on_message(self, message):
        try:
            msg = json.loads(message)
        except :
            pass

        event = msg['event']
        data  = msg.get('data', None)
        txid  = msg.get('id', None)

        logging.debug("[%s] EVENT = %s  DATA = %r" % (txid, event, data))

        result = None
        for handler in self._events.get(event, []):
            if not data:
                result = handler(self.session)
            else:
                result = handler(self.session, **data)

        if txid:
            response = {
                'id'    : txid,
                'event' : event,
                'data'  : result
            }
            self.send(response)

        # self.emit(kwargs['event'], kwargs['data'])

    @classmethod
    def notify(cls, event, data):
        message = {'event': event, 'data' : data}
        if cls.master_session:
            cls.master_session.broadcast(cls.listeners, message)

BacksyncRouter = SockJSRouter(BacksyncChannel, '/backsync')
