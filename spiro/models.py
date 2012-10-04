import logging
import uuid
from redisco import models
import time, hashlib
from datetime import datetime
#from blinker import Signal
from spiro import signals

#
#
#
#
class Field(object):
    value   = None
    default = None

    def __init__(self, value=None, default=None):
        self.value = value
        self.default = default

class BackboneModel(object):
    """This model class will mimic the Backbone Model class to make usage more 
       consistent across JavaScript and Python.
    """
    _isNew    = True

    def __init__(self, *args, **kwargs):
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
        # TODO - fix isnew
        signals.post_save.send(self.__class__, instance=self, created=True)

        # TODO - self.send_update(self, created=isNew)

    def destroy(self, *args, **kwargs):
        pass
        # super(NotifyBase, self).delete(*args, **kwargs)
        ## signals.post_delete.send(self.__class__, instance=self)

        # TODO - self.send_delete(self)

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

#
#
class LogEvent(BackboneModel):
    def __init__(self, msg):
        self.time = datetime.now()
        self.id = hashlib.md5("%f" % time.time()).hexdigest()
        self.message = msg

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
#  Currently stored in Redis, not sure that's the best idea, but for now.
#
class DomainRestriction(models.Model):
    domain = models.Attribute(required=True)

class Settings(models.Model):
    crawl_delay     = models.FloatField(default=1.0)
    max_fetchers    = models.IntegerField(default=100)
    follow_links    = models.BooleanField(default=True)
    crawler_running = models.BooleanField(default=True)

    def _initialize_id(self):
        self.id = 1

    OBJS = {}

    @classmethod
    def singleton(cls, id=1):
        """
          There should only be one settings object in the system, this makes
          it easier to read/write it without worrying about who's doing what
        """
        id = int(id)

        if id in cls.OBJS:
            return cls.OBJS[id]

        obj = cls.objects.get_by_id(id)

        if obj is None:
            obj = cls()
            obj.save()
        cls.OBJS[id] = obj

        return obj
