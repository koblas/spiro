from spiro.web import BacksyncChannel
from sockjs.tornado import SockJSRouter, SockJSConnection

class BacksyncModelRouter(BacksyncChannel):
    MODELS = {}

    @classmethod
    def register(cls, name, handler):
        cls.MODELS[name] = handler

    def instance(self, name):
        return self.MODELS.get(name, None)

    def on_open(self, request):
        for cls in self.MODELS.values():
            obj = cls(self.session)
            if hasattr(obj, 'on_open'):
                obj.on_open()

    def on_close(self):
        for cls in self.MODELS.values():
            obj = cls(self.session)
            if hasattr(obj, 'on_close'):
                obj.on_close()

class BacksyncHandler(object):
    model = None

    def __init__(self, session):
        self.session = session

    def read(self, *args, **kwargs):
        return [msg.serialize() for msg in self.model.find()]

    def upsert(self, *args, **kwargs):
        obj = self.model.find(**kwargs)
        if obj is None:
            obj = self.model(*args, **kwargs)
        else:
            obj.set(**kwargs)
        obj.save()
        return obj.serialize()

    def delete(self, *args, **kwargs):
        obj = self.model.find(**kwargs)
        obj.destroy(**kwargs)
        return {}

class backsync(object):
    """Decorator"""

    def __init__(self, name=None):
        self.name = name

    def __call__(self, klass):
        name = self.name or klass.__name__
        self.klass = klass
        BacksyncModelRouter.register(name, klass)
        return klass

BacksyncRouter = SockJSRouter(BacksyncModelRouter, '/backsync')
