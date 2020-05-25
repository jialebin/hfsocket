import logging
from datetime import datetime
import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.web
from tornado.options import define, options

from Setting import setting
from handlers.urls import urls

# 定义端口
define("port", default=8001, help="run port", type=int, )
define("debug", default=True, help=" run for debug", type=bool)
options.parse_command_line()

# 日志记录位置
options.log_file_prefix = "logs/hf_websocket.log"
# 日志等级默认为info
options.logging = "debug" if options.debug else "info"


# 日志输出形式设置
class LogFormatter(tornado.log.LogFormatter):

    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(filename)s:%(module)s:%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s '
                '%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def main():
    options.parse_command_line()
    if options.debug:
        setting['debug'] = True
    else:
        setting['debug'] = False
    # 添加日志格式
    [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
    app = tornado.web.Application(handlers=urls, **setting)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    logging.info("start server run...")
    logging.info("debug={}".format(app.settings['debug']))
    logging.info("port={}".format(options.port))
    logging.info("datetime={}".format(datetime.now()))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
