import json
from typing import Any

import tornado.websocket
import tornado.web
from pycket.session import SessionMixin
import re

from libs.db.dbsession import dbSession


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
            return None
        else:
            return None

    def initialize(self) -> None:
        self.db = dbSession

    def on_finish(self) -> None:
        self.db.close()
