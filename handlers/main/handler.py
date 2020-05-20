import json
from datetime import datetime

from sqlalchemy.orm import Query
from tornado.iostream import StreamClosedError
from tornado.websocket import WebSocketClosedError

from models.chat_log import ChatLog
from sqlalchemy import or_
import urllib.parse
import uuid
from typing import (
    Optional,
    Awaitable, Union,
)

from handlers.base.base_handler import BaseWebSocket, BaseHandler
from libs.RequestMainSDK import GetUserPub
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
        # 通过token获取用户
        token = self.get_cookie("token", "")
        if not token:
            self.send_error({"type": "message", "message": "用户错误"})
            super(ChatSocket, self).close()
            return
        else:
            self.user = GetUserPub().get_user(token)
        ChatSocket.waiters[self.user.get("id")] = self

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
    def send_updates(cls, chat):
        """
        将接受到的用户消息发送到所有客服手中
        :param chat:
        :return:
        """
        # chat = json.loads(chat)
        for waiter in AdminChatSocket.waiters:
            try:
                waiter.set_header("Content-Type", "application/json")
                waiter.write_message(chat)
            except WebSocketClosedError as e:
                logger.error("socket is closed")
            except StreamClosedError as e:
                logger.error("Error sending message", exc_info=True)

    def on_message(self, message: Union[str, bytes]):
        """
        当接收到websocket信息时的处理函数
        :param message:
        :return:
        """
        logger.debug('got massage %r')
        ChatSocket.send_updates(message)


class AdminChatSocket(BaseWebSocket):
    waiters = dict()
    cache = []
    cache_size = 200

    def check_origin(self, origin: str) -> bool:
        """
        解决跨域问题
        :param origin:
        :return:
        """
        parsed_origin = urllib.parse.urlparse(origin)
        logging.info(parsed_origin)
        return parsed_origin.netloc.endswith(".hfyt365.com")
        # return True

    def open(self, *args: str, **kwargs: str):
        """
        当有websocket链接时的操作
        :param args:
        :param kwargs:
        :return:
        """
        # 通过token获取用户
        ChatSocket.waiters[self.user.get("id")] = self

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
    def send_updates(cls, chat, receiver):
        """
        将接受到的客服消息转发发送到用户手中手中
        :param chat: 消息
        :param receiver: 接受者
        :return:
        """
        waiter = ChatSocket.waiters.get(receiver)
        try:
            waiter.set_header("Content-Type", "application/json")
            waiter.write_message(chat)
        except WebSocketClosedError as e:
            logger.error("socket is closed")
        except StreamClosedError as e:
            logger.error("Error sending message", exc_info=True)

    def on_message(self, message: Union[str, bytes]):
        """
        当接收到客服websocket信息时的处理函数
        :param message:
        :return:
        """
        logger.debug('got massage %r')
        message = json.loads(message)
        receiver = message['receiver']
        del message["receiver"]
        AdminChatSocket.send_updates(message, receiver)


class ChatLogHandler(BaseHandler):
    """获取历史聊天记录接口"""

    def get(self):
        user = self.get_argument('user', "")
        if not user:
            self.finish("参数错误")
            return
        chat_log = self.db.query(ChatLog).filter(or_(ChatLog.receiver_id == user, ChatLog.sender_id == user)).order_by(
            ChatLog.create_time).all()
        chat_logs = []
        for chat in chat_log:
            chat_logs.append(
                {
                    "receiver": chat.receiver_id,
                    "sender": chat.sender_id,
                    "type": chat.type,
                    "create_time": chat.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "message": chat.message
                }
            )
        self.write(json.dumps(chat_logs))
        self.set_header("Content-Type", "application/json")
