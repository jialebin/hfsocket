from handlers.urls import url
from .handler import MainHandler, ChatSocket, AdminChatSocket, ChatLogHandler, LoginHandler
urls = [
    (r'/', MainHandler),
    (r'/socket', ChatSocket),
    (r'/admin/socket', AdminChatSocket),
    (r'/chat/log', ChatLogHandler),
    (r'/login', LoginHandler),
]