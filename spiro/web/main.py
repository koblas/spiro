import tornado.web
import json
import urlparse
import time
from spiro import signals
from spiro.models import LogEvent
from spiro.web.route import route

LOG_LINES = []
token = int(round(time.time() * 1000))

class RedirectHandler(tornado.web.RequestHandler):
    def get(self, path):
        return self.redirect('/#' + path)

@route("/")
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html", production=False)

@route("/data/Crawl(?:/(.*)|)$")
class CrawlDataHandler(tornado.web.RequestHandler):
    def post(self, id=None):
        url = self.get_argument('url')

        try:
            p = urlparse.urlparse(url)

            self.application.work_queue.add(p.netloc, url)
        
            LogEvent("Added %s" % url).save()
        except Exception as e:
            print e
            LogEvent("Bad URL Syntax %s" % url).save()

        self.finish({})

@route("/data/CrawlerState(?:/(.*)|)$")
class CrawlerStateHandler(tornado.web.RequestHandler):
    def get(self, id=None):
        self.finish({
            id: 1,
            'crawler_running': self.application.crawler_running,
        })

    def post(self, id=None):
        data = json.loads(self.request.body)
        if 'crawler_running' in data:
            self.application.crawler_running = data['crawler_running']
        self.finish({})

@route("/data/LogEntries(?:/(.*)|)$")
class LogEntriesDataHandler(tornado.web.RequestHandler):
    def get(self, id=None):
        try:
            rtok = int(self.get_argument('token', None))
        except:
            rtok = 0
        items = [{ 'token': token, 'message': obj[1].message } for obj in LOG_LINES if obj[0] > rtok]
        return self.finish(json.dumps(items))

@route("/data/Queue(?:/(.*)|)$")
class QueueDataHandler(tornado.web.RequestHandler):
    @staticmethod
    def _key(pair):
        val = pair[0]
        if val.startswith('www.'):
            val = val[4:]
        return val
        
    def get(self, id=None):
        items = []
        for item in sorted(self.application.work_queue, key=self._key):
            items.append({
                'host' : item[0],
                'count' : item[1],
            })
        return self.finish(json.dumps(items))

def update_logs(*args, **kwargs):
    global token
    token = int(round(time.time() * 1000))
    LOG_LINES.append((token, kwargs['instance']))

signals.post_save.connect(update_logs, sender=LogEvent)
