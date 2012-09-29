import tornado.web
import json
import time
from spiro import signals
from spiro.models import LogEvent

LOG_LINES = []
token = int(round(time.time() * 1000))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html", production=False)

class DataHandler(tornado.web.RequestHandler):
    def get(self, table):
        if table == 'LogEntries':
            try:
                rtok = int(self.get_argument('token', None))
            except:
                rtok = 0
            items = [{ 'token': token, 'message': obj[1].message } for obj in LOG_LINES if obj[0] > rtok]
            return self.finish(json.dumps(items))
        self.finish({})

    def post(self, table):
        if table == 'Crawl':
            url = self.get_argument('url')
            self.application.work_queue.add(url)

        self.finish({})

def update_logs(*args, **kwargs):
    global token
    token = int(round(time.time() * 1000))
    LOG_LINES.append((token, kwargs['instance']))

signals.post_save.connect(update_logs, sender=LogEvent)
