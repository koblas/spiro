import tornado.web
from tornado import gen
from spiro.processor.robots import RobotCheck
import json
import urlparse
import time
from spiro import signals
from spiro.task import Task
from spiro.models import LogEvent, Settings, RobotRule
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

#
#  Post a URL to be crawled
#
@route("/data/Crawl(?:/(.*)|)$")
class CrawlDataHandler(tornado.web.RequestHandler):
    def post(self, id=None):
        url = self.get_argument('url')

        try:
            if not url.startswith('http://'):
                url = "http://%s" % url

            task = Task(url, force=True)

            self.application.work_queue.add(task)

            self.application.user_settings.domain_restriction.add(task.url_host)
        
            LogEvent("Added %s" % url).save()
        except Exception as e:
            print e
            LogEvent("Bad URL Syntax %s" % url).save()

        self.finish({})

#
#
#
@route("/data/Settings(?:/(.*)|)$")
class SettingsHandler(tornado.web.RequestHandler):
    def _get_obj(self, id):
        return Settings.singleton(id)

    def get(self, id=1):
        obj = self._get_obj(id)

        vals = { 'id' : obj.id }
        vals.update(obj.attributes_dict)

        self.finish(vals)

    def put(self, id):
        data = json.loads(self.request.body)
        obj  = self._get_obj(id)

        if 'max_fetchers' in data:
            obj.max_fetchers = int(data['max_fetchers'])
        if 'crawl_delay' in data:
            obj.crawl_delay = float(data['crawl_delay'])
            self.application.work_queue.default_delay = obj.crawl_delay
        if 'follow_links' in data:
            obj.follow_links = data['follow_links']
        if 'crawler_running' in data:
            obj.crawler_running = data['crawler_running']

        if obj.save() is not True:
            tornado.web.HTTPError(404)

        self.finish({})

#
#  Get log events
#
@route("/data/LogEntries(?:/(.*)|)$")
class LogEntriesDataHandler(tornado.web.RequestHandler):
    def get(self, id=None):
        try:
            rtok = int(self.get_argument('token', None))
        except:
            rtok = 0
        items = [{ 'token': token, 'message': obj[1].message } for obj in LOG_LINES if obj[0] > rtok]
        return self.finish(json.dumps(items))

#
#  Current Crawl Queue
#
@route("/data/Queue(?:/(.*)|)$")
class QueueDataHandler(tornado.web.RequestHandler):
    @staticmethod
    def _key(pair):
        val = pair[0]
        if val.startswith('www.'):
            val = val[4:]
        return val
        
    @tornado.web.asynchronous
    @gen.engine
    def get(self, id=None):
        items = []
        queue_items = yield gen.Task(self.application.work_queue.items)
        for item in sorted(queue_items, key=self._key):
            items.append({
                'host'  : item[0],
                'count' : item[1],
                'total' : item[2],
            })
        self.finish(json.dumps(items))

#
#
#
@route("/data/RobotRule(?:/(.*)|)$")
class RobotRuleDataHandler(tornado.web.RequestHandler):
    ID = 0
    RULES = []

    def get(self, id=None):
        items =[item.serialize() for item in RobotRule.objects.all()]
        return self.finish(json.dumps(items))

    @tornado.web.asynchronous
    @gen.engine
    def post(self, id=None):
        obj = json.loads(self.request.body)

        obj['flag'] = bool(obj['flag'])
        rule = RobotRule(**obj)
        rule.save()

        RobotCheck.remove_site(rule.site)

        self.finish(rule.serialize())

    @tornado.web.asynchronous
    @gen.engine
    def delete(self, id=None):
        rule = RobotRule.objects(id=id).get()

        RobotCheck.remove_site(rule.site)

        rule.delete()

        self.finish({})


#
#
#
def update_logs(*args, **kwargs):
    global token
    token = int(round(time.time() * 1000))
    LOG_LINES.append((token, kwargs['instance']))

signals.post_save.connect(update_logs, sender=LogEvent)


#
#
#
def update_logs(*args, **kwargs):
    global token
    token = int(round(time.time() * 1000))
    LOG_LINES.append((token, kwargs['instance']))

signals.post_save.connect(update_logs, sender=LogEvent)
