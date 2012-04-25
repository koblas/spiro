import logging
import uuid
import time, hashlib
from datetime import datetime
from blinker import Signal
from spiro.signal import client_message
from spiro.web import BacksyncChannel

class Field(object):
    value   = None
    default = None

    def __init__(self, value=None, default=None):
        self.value = value
        self.default = default

class backsync(object):
    def __init__(self, name=None):
        self.name = name

    def __call__(self, klass):
        name = self.name or klass.__name__
        self.klass = klass
        BacksyncChannel.register(name, klass)
        klass.send_update = self.send_update
        klass.send_delete = self.send_delete
        return klass

    def send_update(self, instance, created=False):
        # print "SENDING UPSERT"
        name = self.name or self.klass.__name__
        BacksyncChannel.notify("%s:upsert" % (name), instance.serialize())

    def send_delete(self, instance):
        # print "SENDING DELET..."
        name = self.name or self.klass.__name__
        BacksyncChannel.notify("%s:delete" % (name), instance.serialize())


# client_message.signal('Task:create').connect(test)

class SignalHolder(object):
    def __init__(self):
        self.post_save     = Signal()
        self.post_delete   = Signal()
        self.client_update = Signal()

signals = SignalHolder()

class BackboneModel(object):
    """This model class will mimic the Backbone Model class to make usage more 
       consistent across JavaScript and Python.
    """
    _isNew    = True

    def __init__(self, session, *args, **kwargs):
        self._fields = {}
        for field in dir(self):
            v = getattr(self, field)
            if isinstance(v, Field):
                self._fields[field] = v
                if hasattr(v, 'default') and callable(v.default):
                    setattr(self, field, v.default())
                else:
                    setattr(self, field, getattr(v, 'default', None))
        self.set(**kwargs)

    def set(self, *args, **kwargs):
        for field, value in kwargs.items():
            if field in self._fields:
                setattr(self, field, value)
        return self

    def save(self, *args, **kwargs):
        # super(Model, self).save(*args, **kwargs)
        isNew = self._isNew
        self._isNew = False
        ## signals.post_save.send(self.__class__, instance=self, created=True)
        self.send_update(self, created=isNew)

    def destroy(self, *args, **kwargs):
        # super(NotifyBase, self).delete(*args, **kwargs)
        ## signals.post_delete.send(self.__class__, instance=self)
        self.send_delete(self)

    @classmethod
    def find(self, **kwargs):
        """Find an object based on the object parameters passed"""
        return None

    def validate(self, **kwargs):
        return None

    def serialize(self):
        data = {}
        for field in self._fields:
            data[field] = getattr(self, field)
        return data

    # HMM....

    @classmethod
    def handle_read(cls, session, *args, **kwargs):
        v = [msg.serialize() for msg in cls.find(session)]
        print cls, v
        return v

    # TODO - Make it all upsert
    @classmethod
    def handle_upsert(cls, session, *args, **kwargs):
        obj = cls.find(session, **kwargs)
        if obj is None:
            obj = cls(session, *args, **kwargs)
        else:
            obj.set(**kwargs)
        obj.save()
        return obj.serialize()

    @classmethod
    def handle_delete(cls, session, *args, **kwargs):
        obj = cls.find(session, **kwargs)
        obj.destroy(**kwargs)
        return {}
#
#
#
class LogEvent(BackboneModel):
    def __init__(self, msg):
        self.time = datetime.now()
        self.id = hashlib.md5("%f" % time.time()).hexdigest()
        self.msg = msg

    def serialize(self):
        return {
            'id' : self.id,
            'datetime' : self.time.strftime("%Y-%m-%d %H:%M:%S"),
            'msg' : self.msg,
        }

class SeedTask(BackboneModel):
    def set(self, url=None, **kwargs):
        self.url = url


#
#
#
@backsync('User')
class ChatUser(BackboneModel):
    USERS = {}

    guid     = Field(default=lambda:str(uuid.uuid4()))
    screenName = Field(default='Anonymous')

    def save(self, *args, **kwargs):
        self.USERS.append(self)
        super(ChatUser, self).save(*args, **kwargs)

    def destroy(self, *args, **kwargs):
        self.USERS.remove(self)
        super(ChatUser, self).destroy(*args, **kwargs)

    @classmethod
    def find(cls, session, **kwargs):
        guid = kwargs.get('guid')
        if guid:
            for m in cls.USERS.values():
                if m.guid == guid:
                    return m
            return None
        return cls.USERS.values()

    @classmethod
    def handle_open(cls, session):
        print "***** HANDLE OPEN"

    @classmethod
    def handle_close(cls, session):
        print "***** HANDLE CLOSE"
        del cls.USERS[session]


@backsync()
class ChatMessage(BackboneModel):
    MESSAGES = []
    COUNTER  = 1000

    guid       = Field(default=lambda:str(uuid.uuid4()))
    userId     = Field()
    message    = Field(default='')
    color      = Field(default='black')
    screenName = Field(default='anonymous')

    def save(self, *args, **kwargs):
        self.MESSAGES.append(self)
        super(ChatMessage, self).save(*args, **kwargs)

    def destroy(self, *args, **kwargs):
        self.MESSAGES.remove(self)
        super(ChatMessage, self).destroy(*args, **kwargs)

    @classmethod
    def find(cls, session, **kwargs):
        guid = kwargs.get('guid')
        if guid:
            for m in cls.MESSAGES:
                if m.guid == guid:
                    return m
            return None
        return cls.MESSAGES

ChatMessage(message="message one").save()
ChatMessage(message="message two").save()
ChatMessage(message="message three").save()
