#!/usr/bin/env python

import logging
import os
import mongoengine
import settings
from datetime import timedelta
import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado import gen
from tornado.options import define, options

define("debug", default=False, help="run in debug mode", type=bool)
define("prefork", default=False, help="pre-fork across all CPUs", type=bool)
define("port", default=9000, help="run on the given port", type=int)
define("bootstrap", default=False, help="Run the bootstrap model commands")

from spiro.web.route import route
from spiro.web.main import RedirectHandler
from spiro.queue import RedisQueue
from spiro.pipeline import Pipeline
from spiro import redis
from spiro import models

#
#
#
class Application(tornado.web.Application):
    def __init__(self):
        if options.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        app_settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "web", "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "web", "static"),
        )

        mongoengine.connect(settings.STORE_BUCKET)

        self.user_settings = models.Settings.singleton()
        self.redis = redis.Client()
        self.redis.connect()
        self.work_queue = RedisQueue(self.redis)
        self.work_queue.default_delay = self.user_settings.crawl_delay

        routes = route.get_routes()
        # Hast to be the last route...
        routes.extend([
                    (r"/(.+)", RedirectHandler),
                ])

        super(Application, self).__init__(routes, **app_settings)

        self.ioloop  = tornado.ioloop.IOLoop.instance()

class Worker(object):
    def __init__(self, app, settings, queue, io_loop=None):
        self.app      = app
        self.ioloop   = io_loop or tornado.ioloop.IOLoop.instance()
        self.queue    = queue
        self.pipeline = Pipeline(settings.PIPELINE, settings=settings, work_queue=queue, user_settings=app.user_settings)
        self.running_fetchers  = 0
        self.total_fetch_count = 0
        self.ioloop.add_callback(self.loop)

    @gen.engine
    def loop(self):
        if not self.queue or not self.app.user_settings.crawler_running:
            self.ioloop.add_timeout(timedelta(seconds=1), self.loop)
            return

        task = None
        try:
            task, complete_cb = yield gen.Task(self.queue.pop)
        except Exception as e:
            self.ioloop.add_timeout(timedelta(seconds=1), self.loop)

        if not task:
            self.ioloop.add_timeout(timedelta(seconds=1), self.loop)
            return

        logging.debug("Staring task url=%s" % task.url)

        self.running_fetchers  += 1

        yield gen.Task(self.pipeline.process, task)
        complete_cb(True, task)

        self.total_fetch_count += 1
        self.running_fetchers  -= 1

        if task.response:
            models.LogEvent("Crawled %d %s" % (task.response.code, task.url)).save()
        else:
            models.LogEvent("NOT Crawled %s" % (task.url)).save()
        logging.debug("Finished task url=%s" % task.url)

        self.ioloop.add_callback(self.loop)

def application():
    tornado.options.parse_command_line()

    #queue    = SpiderQueue()
    app      = Application()
    worker   = Worker(app, settings, app.work_queue)

    http_server = tornado.httpserver.HTTPServer(app)

    print "Starting tornado on port", options.port
    if options.prefork:
        print "\tpre-forking"
        http_server.bind(options.port)
        http_server.start()
    else:
        http_server.listen(options.port)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

def main():
    application()

if __name__ == '__main__':
    main()
