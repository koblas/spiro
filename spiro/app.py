#!/usr/bin/env python

import logging
from spiro.signal import client_message
import os
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

from spiro.web import MainHandler, DataHandler
from spiro.queue import SimpleQueue
from spiro.pipeline import Pipeline
from spiro.task import Task
from spiro import models

#
#
#
class Application(tornado.web.Application):
    def __init__(self, work_queue):
        handlers = [
            (r"/", MainHandler),
            (r"/data/(.+)", DataHandler),
        ]

        app_settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "web", "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "web", "static"),
        )

        self.work_queue = work_queue

        super(Application, self).__init__(handlers, **app_settings)

        self.ioloop  = tornado.ioloop.IOLoop.instance()
        self.ioloop.add_timeout(timedelta(seconds=1), self.ping)

    def ping(self):
        #ClientChannel.emit_log_event("HI DAVE")

        import time, hashlib
        eid = hashlib.md5("%f" % time.time()).hexdigest()

        # self.channel.send("logevents:create", {'id': eid, 'msg': 'hi dave! - %d' % time.time()})

        self.ioloop.add_timeout(timedelta(seconds=1), self.ping)
        pass
        

class Worker(object):
    def __init__(self, app, settings, queue, io_loop=None):
        self.app      = app
        self.ioloop   = io_loop or tornado.ioloop.IOLoop.instance()
        self.queue    = queue
        self.pipeline = Pipeline(settings.PIPELINE, settings=settings, work_queue=queue)
        self.loop()

    @gen.engine
    def loop(self):
        if self.queue.empty():
            self.ioloop.add_timeout(timedelta(seconds=1), self.loop)
            return

        url = self.queue.pop()
        if url:
            print "URL = ", url
            task = Task(url)

            yield gen.Task(self.pipeline.process, task)

            #self.app.channel.send("logevents:create", models.LogEvent("Crawled %s" % url).serialize())

            models.LogEvent("Crawled %s" % url).save()

        self.ioloop.add_callback(self.loop)

def main():
    tornado.options.parse_command_line()

    queue    = SimpleQueue()
    app      = Application(queue)
    worker   = Worker(app, settings, queue)

    http_server = tornado.httpserver.HTTPServer(app)

    def add_item(sender, instance=None, **kwargs):
        logging.debug("ADDING TO QUEUE %s " % instance.url)
        queue.add(instance.url)

    # models.signals.post_save.connect(add_item, sender=models.SeedTask)

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

if __name__ == '__main__':
    main()
