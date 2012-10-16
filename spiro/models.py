#import logging
import mongoengine
import time, hashlib
from datetime import datetime
from mongoengine import signals

#
#
#
class LogEvent(object):
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

    def save(self):
        signals.post_save.send(self.__class__, document=self, created=True)

#
#  MongoEngine based documents
#
class EngineMixin(object):
    def serialize(self):
        from bson.objectid import ObjectId

        result = {}

        for k in self._fields.keys():
            if k in ('password'):
                continue

            v = getattr(self, k)
            if isinstance(v, ObjectId):
                result[k] = str(v)
            else:
                result[k] = v

        return result

class RobotRule(mongoengine.Document, EngineMixin):
    meta = {
        'collection'        : 'RobotRule',
    }

    flag       = mongoengine.BooleanField()
    site       = mongoengine.StringField()
    path       = mongoengine.StringField()

class DomainHelper(object):
    def __init__(self):
        self.data = None

    def __contains__(self, val):
        if self.data is None:
            self.data = {obj.domain for obj in DomainConfiguration.objects()}
        return val in self.data

    def add(self, val):
        obj = DomainConfiguration(domain=val)
        obj.save()
        if self.data is None:
            self.data = {obj.domain for obj in DomainConfiguration.objects()}
        self.data.add(val)

class DomainConfiguration(mongoengine.Document, EngineMixin):
    meta = {
        'collection'        : 'DomainConfiguration',
    }

    domain       = mongoengine.StringField(unique=True)
    enabled      = mongoengine.BooleanField(default=True)
    crawl_delay  = mongoengine.FloatField(default=None)

class Settings(mongoengine.Document, EngineMixin):
    meta = {
        'collection'        : 'Settings',
    }

    guid            = mongoengine.StringField()
    crawl_delay     = mongoengine.FloatField(default=1.0)
    max_fetchers    = mongoengine.IntField(default=100)
    follow_links    = mongoengine.BooleanField(default=True)
    crawler_running = mongoengine.BooleanField(default=True)
    _domain_helper  = DomainHelper()

    @property
    def domain_restriction(self):
        return self._domain_helper

    @classmethod
    def singleton(cls, id=1):
        """
          There should only be one settings object in the system, this makes
          it easier to read/write it without worrying about who's doing what
        """
        id = str(id)

        try:
            obj = cls.objects.get(guid=id)
        except cls.DoesNotExist:
            obj = cls(guid=id)
            obj.save()

        return obj
