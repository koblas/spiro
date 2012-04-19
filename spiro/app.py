#!/usr/bin/env python

import os
import settings
import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado.options import define, options

define("debug", default=False, help="run in debug mode", type=bool)
define("prefork", default=False, help="pre-fork across all CPUs", type=bool)
define("port", default=9000, help="run on the given port", type=int)
define("bootstrap", default=False, help="Run the bootstrap model commands")

from spiro.web import MainHandler
from spiro.fetcher import Fetcher, Queue
from spiro.pipeline import Pipeline

class Application(tornado.web.Application):
    def __init__(self, work_queue):
        handlers = (
            (r"/", MainHandler),
        )

        app_settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "web", "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "web", "static"),
        )

        self.work_queue = work_queue

        super(Application, self).__init__(handlers, **app_settings)

def main():
    tornado.options.parse_command_line()

    queue    = Queue()
    pipeline = Pipeline(settings.EXTRACT_PIPELINE, settings=settings, work_queue=queue)
    fetcher  = Fetcher(queue=queue, process=pipeline)

    http_server = tornado.httpserver.HTTPServer(Application(queue))

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
