import time, hashlib
from datetime import datetime

class LogEvent(object):
    
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
