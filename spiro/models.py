#import logging
import mongoengine
import time, hashlib
from datetime import datetime
from mongoengine import signals
from collections import defaultdict

class PageStats(object):
    BUCKET_SIZE = 60    # Accumulate 60 seconds worth of data in one bucket

    PPS = defaultdict(int)
    BPS = defaultdict(int)

    @classmethod
    def now(cls):
        tnow = int(time.time())
        return tnow - (tnow % cls.BUCKET_SIZE);

    @classmethod
    def crawled(cls, code, bytes):
        tnow = cls.now()

        cls.PPS[tnow] += 1
        cls.BPS[tnow] += bytes

    @classmethod
    def stats(cls, timeframe=60):
        """Print the crawl stats - default for the last hour"""
        pps = []
        bps = []

        # Get the current time
        tnow = cls.now()

        for tval in range(tnow - timeframe * cls.BUCKET_SIZE, tnow + cls.BUCKET_SIZE, cls.BUCKET_SIZE):
            if tval in cls.PPS:
                pps.append((tval * 1000, float("%.1f" % (cls.PPS[tval] / float(cls.BUCKET_SIZE)))))
            if tval in cls.BPS:
                bps.append((tval * 1000, int(cls.BPS[tval] / float(cls.BUCKET_SIZE))))

        return dict(pps=pps, bps=bps)

#
#
#
class LogEvent(object):
    def __init__(self, msg):
        self.time = datetime.now()
        self.ftime = self.time.strftime("%Y-%m-%d %H:%M:%S")
        self.id = hashlib.md5("%f" % time.time()).hexdigest()
        self.message = msg

    def serialize(self):
        ts = self.time.strftime("%Y-%m-%d %H:%M:%S")
        return {
            'id' : self.id,
            'datetime' : self.time.strftime("%Y-%m-%d %H:%M:%S"),
            'msg' : "%s %s" % (ts, self.msg),
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
    domain_concurrency = mongoengine.IntField(default=2)
    follow_links    = mongoengine.BooleanField(default=True)
    crawler_running = mongoengine.BooleanField(default=True)
    _domain_helper  = DomainHelper()

    OBJS = {}

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

        if id not in cls.OBJS:
            try:
                cls.OBJS[id] = cls.objects.get(guid=id)
            except cls.DoesNotExist:
                obj = cls(guid=id)
                obj.save()
                cls.OBJS[id] = obj

        return cls.OBJS[id]
