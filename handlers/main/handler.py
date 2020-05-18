from handlers.base.base_handler import BaseWebSocket, BaseHandler


class MainHandler(BaseHandler):
    def get(self):
        self.write("测试主页函数")
        # self.render()
