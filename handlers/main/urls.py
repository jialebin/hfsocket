from handlers.urls import url
from .handler import MainHandler, ChatSocket
urls = [
    (r'/', MainHandler),
    (r'/', ChatSocket)
]