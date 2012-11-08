from datetime import datetime
import logging
import tornado.web
from tornado import gen
import json
import time
from spiro.metrics import systemMetrics
from spiro.task import Task
from spiro.models import signals, LogEvent, Settings, RobotRule, DomainConfiguration, PageStats
from spiro.web.route import route

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
            logging.error("Exception in Adding URL", e) 
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

        self.finish(obj.serialize())

    def put(self, id):
        data = json.loads(self.request.body)
        obj  = self._get_obj(id)

        if 'max_fetchers' in data:
            obj.max_fetchers = int(data['max_fetchers'])
        if 'domain_concurrency' in data:
            obj.domain_concurrency = int(data['domain_concurrency'])
        if 'crawl_delay' in data:
            obj.crawl_delay = float(data['crawl_delay'])
        if 'follow_links' in data:
            obj.follow_links = data['follow_links']
        if 'crawler_running' in data:
            obj.crawler_running = data['crawler_running']

        if obj.save() is not True:
            tornado.web.HTTPError(404)

        self.finish(obj.serialize())

#
#  Get log events
#
@route("/data/LogEntries(?:/(.*)|)$")
class LogEntriesDataHandler(tornado.web.RequestHandler):
    LOG_LINES = []
    token = int(round(time.time() * 1000))

    @classmethod
    def update_logs(cls, sender, document, *args, **kwargs):
        cls.token = int(round(time.time() * 1000))
        cls.LOG_LINES.append((cls.token, document))
        if len(cls.LOG_LINES) > 200:
            del cls.LOG_LINES[0:-200]

    def get(self, id=None):
        try:
            rtok = int(self.get_argument('token', None))
        except:
            rtok = 0

        items = [{ 'tval': (obj[1].time-datetime(1970,1,1)).total_seconds(), 
                   'time': obj[1].ftime, 
                   'message': obj[1].message 
               } for obj in self.LOG_LINES if obj[0] > rtok]
        return self.finish(json.dumps({
                                'token' : self.token,
                                'items' : items,
                            }))

signals.post_save.connect(LogEntriesDataHandler.update_logs, sender=LogEvent)

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
                'ave_resp' : float("%.2f" % systemMetrics.ave('response:%s' % item[0])),
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

        self.finish(rule.serialize())

    @tornado.web.asynchronous
    @gen.engine
    def delete(self, id=None):
        rule = RobotRule.objects(id=id).get()

        rule.delete()

        self.finish({})

#
#
#
@route("/data/DomainConfiguration(?:/(.*)|)$")
class DomainRestrictionDataHandler(tornado.web.RequestHandler):
    ID = 0
    RULES = []

    def get(self, id=None):
        items =[item.serialize() for item in DomainConfiguration.objects.all()]
        return self.finish(json.dumps(items))

    @tornado.web.asynchronous
    @gen.engine
    def post(self, id=None):
        obj = json.loads(self.request.body)

        model = DomainConfiguration(**obj)
        model.save()

        self.finish(model.serialize())

    @tornado.web.asynchronous
    @gen.engine
    def delete(self, id=None):
        model = DomainConfiguration.objects(id=id).get()

        model.delete()

        self.finish({})

#
#
#
@route("/data/stats/$")
class StatsDataHandler(tornado.web.RequestHandler):
    def get(self):
        return self.finish(PageStats.stats())

@route("/data/stats/pipeline$")
class PipelineStatsDataHandler(tornado.web.RequestHandler):
    def get(self):
        metrics = {}
        for k, v in systemMetrics.items():
            if not k.startswith("pipeline:"):
                continue
            _, step, kind = k.split(':')
            if step not in metrics:
                metrics[step] = {}
            if kind == 'calls':
                metrics[step]['calls']  = systemMetrics.value(k)
            elif kind == 'time':
                metrics[step]['median'] = int(systemMetrics.median(k) * 1000)
                metrics[step]['ave']    = int(systemMetrics.ave(k) * 1000)
        if not metrics:
            return self.finish(json.dumps([]))
        else:
            return self.finish(json.dumps( [dict([('id',k)]+list(v.items())) for k, v in metrics.items()] ))
