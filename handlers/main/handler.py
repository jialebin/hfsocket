import json
from datetime import datetime
from json.decoder import JSONDecodeError

from tornado.web import authenticated
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

    @authenticated
    def get(self):
        # self.write("小改一下")
        # self.render()
        logger.debug("客服登录，登录名 = {}".format(self.get_current_user()))
        self.render('index.html')


class LoginHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.redirect(self.get_argument('next', "/"))
            return
        self.render('login.html', next=self.get_argument("next", '/'))

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        if username == 'hfyt_admin' and password == "hfyt67251751":
            self.success_login()
            logger.debug(self.request.headers)
            logger.debug("next = {}".format(self.get_argument('next', "/")))
            self.redirect(self.get_argument('next', "/"))
        else:
            self.write("登录失败")
            self.finish("登录失败")

    def success_login(self):
        self.session.set("username", "行丰客服")


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
        # logging.debug(parsed_origin)
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
        token = self.get_argument("token", None)
        if not token:
            self.write_message({"type": "message", "message": "用户错误"})
            super(ChatSocket, self).close()
            return
        else:
            self.user = GetUserPub().get_user(token)
        open_socket = {
            "type": "message",
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "message": {
                "message": "open websocket",
                "user_name": self.user.get('username'),
                "user_id": self.user.get('id')
            }
        }
        ChatSocket.send_updates(json.dumps(open_socket, ensure_ascii=False))
        ChatSocket.waiters[self.user.get("id")] = {
            "socket": self,
            "username": self.user.get('username'),
            "user_id": self.user.get('id')
        }
        logger.debug("用户链接 --- {}".format(self.user.get("username")))
        self.write_message(
            json.dumps({"type": "str", "message": "链接成功", "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), },
                       ensure_ascii=False))

    def on_close(self) -> None:
        """
        websocket断开时的操作
        :return:
        """
        logger.debug("断开连接 -- {}".format(self.user.get('username')))
        try:
            del ChatSocket.waiters[self.user.get('id')]
        except TypeError:
            pass
        except AttributeError:
            pass
        except KeyError:
            pass
        open_socket = {
            "type": "message",
            "message": {
                "message": "close websocket",
                "user_name": self.user.get('username'),
                "user_id": self.user.get('id')
            }
        }
        ChatSocket.send_updates(json.dumps(open_socket, ensure_ascii=False))

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
        try:
            # waiter.set_header("Content-Type", "application/json")
            try:
                chat = json.loads(chat)
            except JSONDecodeError as e:
                error_socket = {
                    "type": "message",
                    "message": "消息格式错误",
                    "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                cls.write_message(json.dumps(error_socket, ensure_ascii=False))
                return
            chat['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except WebSocketClosedError as e:
            logger.error("socket is closed")
        except StreamClosedError as e:
            logger.error("Error sending message", exc_debug=True)
        for waiter in AdminChatSocket.waiters:
            chat["user_id"] = cls.user.id
            logger.debug("给客服的最终消息{}".format(json.dumps(chat, ensure_ascii=False)))

            waiter.write_message(json.dumps(chat, ensure_ascii=False))

    def on_message(self, message: Union[str, bytes]):
        """
        当接收到websocket信息时的处理函数
        :param message:
        :return:
        """
        # logger.debug('got massage %r')
        logger.debug("用户消息类型{}".format(type(message)))
        logger.debug("用户消息 === {}".format(message))
        # self.write_message(message if isinstance(message, str) else json.dumps(message, ensure_ascii=False))
        # return
        if not message:
            return
        self.create_chat_log(message)
        ChatSocket.send_updates(message)

    def create_chat_log(self, message):
        """
        向数据库保存一条聊天记录
        :param message:
        :return: ChatLog()
        """
        chat_log = ChatLog()
        # logger.debug('message = {}'.format(message))
        try:
            message_dic = json.loads(message)
        except JSONDecodeError:
            return
        chat_log.message = message_dic.get("message")
        chat_log.sender_id = self.user.get('id')
        chat_log.create_time = datetime.now()
        chat_log.type = message_dic.get('type')
        chat_log.create()
        return chat_log


class AdminChatSocket(BaseWebSocket):
    waiters = list()
    cache = []
    cache_size = 200

    def check_origin(self, origin: str) -> bool:
        """
        解决跨域问题
        :param origin:
        :return:
        """
        # parsed_origin = urllib.parse.urlparse(origin)
        # logging.debug(parsed_origin)
        # return parsed_origin.netloc.endswith(".hfyt365.com")
        return True

    def open(self, *args: str, **kwargs: str):
        """
        当有websocket链接时的操作
        :param args:
        :param kwargs:
        :return:
        """
        # 通过token获取用户
        AdminChatSocket.waiters.append(self)
        self.write_message(
            json.dumps(
                {
                    "type": "message",
                    "message": "The users in the link",
                    "users": [
                        {"username": v["username"], "user_id": v["user_id"]}
                        for k, v in ChatSocket.waiters.items()]
                }
            )
        )

    def on_close(self) -> None:
        """
        websocket断开时的操作
        :return:
        """
        try:
            AdminChatSocket.waiters.remove(self)
        except TypeError:
            pass

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
        try:
            # waiter.set_header("Content-Type", "application/json")
            logger.debug("给 {} 发消息 {}".format(receiver, chat))
            waiter = ChatSocket.waiters.get(receiver).get("socket")
            chat['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.debug("给用户的最终消息{}".format(json.dumps(chat, ensure_ascii=False)))
            waiter.write_message(json.dumps(chat, ensure_ascii=False))
        except WebSocketClosedError as e:
            logger.error("socket is closed")
        except StreamClosedError as e:
            logger.error("Error sending message")
        except TypeError:
            pass

    def on_message(self, message: Union[str, bytes]):
        """
        当接收到客服websocket信息时的处理函数
        :param message:
        :return:
        """
        # logger.debug('got massage %r')
        try:
            message = json.loads(message)
        except JSONDecodeError:
            logger.warning("错误数据{}".format(message))
            self.write_message(json.dumps({"type": "message",
                                           "message": '数据错误消息类似：{"receiver":227,"type":"str""message": "发送内容[image,url 均传输字符串，图片为链接暂未实现图片传输]"}'},
                                          ensure_ascii=False))
            return
        receiver = message.get('receiver')
        if not receiver and not isinstance(receiver, int):
            logger.warning("消息错误 {}".format(message))
            return
        del message["receiver"]
        self.create_chat_log(receiver, message)
        AdminChatSocket.send_updates(message, receiver)

    def create_chat_log(self, receiver, message):
        """
        向数据库保存一条聊天记录
        :param receiver: 接收方
        :param message: 消息
        :return: ChatLog()
        """
        chat_log = ChatLog()
        chat_log.message = message.get("message")
        chat_log.receiver_id = receiver
        chat_log.create_time = datetime.now()
        chat_log.type = message.get('type')
        chat_log.create()
        return chat_log


class ChatLogHandler(BaseHandler):
    """获取历史聊天记录接口"""

    def get(self):
        user = self.get_argument('user', "")
        page = self.get_argument('page', '1')
        if not user:
            self.finish("参数错误")
            return
        if not page.isdecimal():
            self.write('输入错误')
            self.finish()
            return
        page = int(page)
        chat_log = self.db.query(ChatLog).filter(or_(ChatLog.receiver_id == user, ChatLog.sender_id == user)).order_by(
            ChatLog.create_time.desc()).slice(20 * (page - 1), 20 * page).all()
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

    def options(self):
        self.set_status(204)
        self.finish()


'''
sqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) \
    (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''id': '20'}, '2020-05-21 16:49:36.257780', '发送内容[image,url 均传输字�' at line 1")

    [SQL: INSERT INTO chat_log (receiver_id, sender_id, create_time, message, type) VALUES (%(receiver_id)s, %(sender_id)s, %(create_time)s, %(message)s, %(type)s)]
    [parameters: {'receiver_id': None, 'sender_id': {'id': 20}, 'create_time': datetime.datetime(2020, 5, 21, 16, 49, 36, 257780), 'message': '发送内容[image,url 均传输字符串，图片为链接暂未实现图片传输', 'type': 'str'}]
    (Background on this error at: http://sqlalche.me/e/f405)
'''
