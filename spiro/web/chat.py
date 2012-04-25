import tornado.web

class ChatHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("chat.html")
