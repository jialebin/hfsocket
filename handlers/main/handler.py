import json
import urllib.parse
import uuid
from typing import (
    Optional,
    Awaitable, Union,
)

from handlers.base.base_handler import BaseWebSocket, BaseHandler

import logging
logger = logging.getLogger()

class MainHandler(BaseHandler):
    def get(self):
        self.write("测试主页函数")
        # self.render()


class ChatSocket(BaseWebSocket):
    waiters = dict()
    cache = []
    cache_size = 200

    def check_origin(self, origin: str) -> bool:
        """
        解决跨域问题
        :param origin:
        :return:
        """
        # parsed_origin = urllib.parse.urlparse(origin)
        # logging.info(parsed_origin)
        # return parsed_origin.netloc.endswith("8080")
        return True

    def open(self, *args: str, **kwargs: str):
        """
        当有websocket链接时的操作
        :param args:
        :param kwargs:
        :return:
        """
        if self.get_current_user():
            self.user = self.get_current_user().name
        else:
            self.user = str(uuid.uuid1())
        ChatSocket.waiters[self.user] = self
        self.write_message({'user': str(self.user)})

    def on_close(self) -> None:
        """
        websocket断开时的操作
        :return:
        """
        del ChatSocket.waiters[self.user]

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat, to: str):
        """
        真正发送用户信息的函数
        :param chat:
        :return:
        """
        # chat = json.loads(chat)
        waiter = cls.waiters[to]
        try:
            waiter.write_message(json.dumps({"user": chat.get("uuid"), "message": chat.get('message')}))
        except:
            logger.error("Error sending message", exc_info=True)

    def on_message(self, message: Union[str, bytes]):
        """
        当接收到websocket信息时的处理函数
        :param message:
        :return:
        """
        logger.debug('got massage %r')
        ChatSocket.send_updates(message)
