import logging
import tornadio2
from blinker import Signal
from spiro.signal import client_message
from spiro.models import signals

from tornadio2 import gen

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

    @classmethod
    def add_event(self, name, handler):
        pass

    #@gen.engine
    #def on_event(self, name, callback=None, args=[], kwargs=dict()):
    #    logging.debug("Received Event: %s - %r" % (name, kwargs))
    #    response = yield gen.Task(client_message.signal(name).send, None, **kwargs)
    #    callback(response)

    def _send_event(self, sender, **kwargs):
        self.emit(kwargs['event'], kwargs['data'])

    @classmethod
    def send(cls, event, data):
        raise "NOT ME"
        print "SENDING: %s %r" % (event, data)
        cls._signal.send(None, event=event, data=data)

ChannelRouter = tornadio2.TornadioRouter(ClientChannel)

def on_model_save(sender, instance=None, **kwargs):
    cname = sender.__name__
    data  = instance.serialize()
    if data:
        if kwargs.get('created', False):
            #ClientChannel.send("%s_Collection:create" % (cname), data)
            ClientChannel.send("%s:create" % (cname), data)
        else:
            ClientChannel.send("%s:%s" % (cname, 'update'), data)

def on_model_delete(sender, instance=None, **kwargs):
    cname = sender.__class__.__name__
    ClientChannel.send("%s:%s" % (cname, 'delete'), instance.serialize())

signals.post_save.connect(on_model_save)
