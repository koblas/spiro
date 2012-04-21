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

from spiro.web import MainHandler, ChannelRouter, ClientChannel
from spiro.queue import SimpleQueue
from spiro.pipeline import Pipeline
from spiro.task import Task

#
#
#
class Application(tornado.web.Application):
    def __init__(self, work_queue):
        handlers = [
            (r"/", MainHandler)
        ]

        ChannelRouter.apply_routes(handlers)

        app_settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "web", "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "web", "static"),
        )


        self.work_queue = work_queue

        super(Application, self).__init__(handlers, **app_settings)

        self.channel = ClientChannel
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
    def __init__(self, settings, queue, io_loop=None):
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

        self.ioloop.add_callback(self.loop)

def main():
    tornado.options.parse_command_line()

    queue    = SimpleQueue()
    worker   = Worker(settings, queue)

    http_server = tornado.httpserver.HTTPServer(Application(queue))

    def add_item(sender, url=None, **kwargs):
        print("ADDING TO QUEUE %s " % url)
        queue.add(url)

    client_message.signal('task:create').connect(add_item)

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
