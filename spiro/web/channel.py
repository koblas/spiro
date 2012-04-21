import logging
import tornadio2
from blinker import Signal
from spiro.signal import client_message

#print "SIGNAL = ", signal
print "ClientChannel signal = ", client_message
#
#
#
class ClientChannel(tornadio2.SocketConnection):
    _signal = Signal()

    def on_open(self, request):
        #print "task:create signal = ", signal('task:create')
        #print "RECEIVERS", signal('task:create').receivers
        self._signal.connect(self._send_event)

    def on_close(self):
        self._signal.disconnect(self._send_event)

    def on_event(self, name, args=[], kwargs=dict()):
        logging.debug("Received Event: %s - %r" % (name, kwargs))
        client_message.signal(name).send(None, **kwargs)

    def _send_event(self, sender, **kwargs):
        self.emit(kwargs['event'], kwargs['data'])

    @classmethod
    def send(cls, event, data):
        cls._signal.send(None, event=event, data=data)

ChannelRouter = tornadio2.TornadioRouter(ClientChannel)
