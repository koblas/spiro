import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html")

    def post(self):
        url = self.get_argument('url')
        self.application.work_queue.add(url)

        self.render("main.html");
