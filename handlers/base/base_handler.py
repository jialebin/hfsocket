import json
from typing import Any

import tornado.websocket
import tornado.web
from pycket.session import SessionMixin
import re

from libs.db.dbsession import dbSession

import logging

logger = logging.getLogger()


class BaseWebSocket(tornado.websocket.WebSocketHandler, SessionMixin):
    """
    所有websocket的基类
    """

    def get_current_user(self) -> Any:
        """
        返回用户，如果不存在返回None
        :return: User/None
        """
        if self.session.get("username"):
            return None
        else:
            return None


class BaseHandler(tornado.web.RequestHandler, SessionMixin):
    """
    所有Handler的基类
    """

    def get_current_user(self) -> Any:
        """
        返回用户，如果不存在返回None
        :return: User/None
        """
        # 查询session中的username
        if self.session.get("username"):
            # 返回user对象
            return self.session.get('username')
        else:
            return None

    def initialize(self) -> None:
        self.db = dbSession

    def on_finish(self) -> None:
        self.db.close()

    # 允许跨域访问的地址
    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type")
        self.set_header("Access-Control-Expose-Headers",
                        "Content-Type")
