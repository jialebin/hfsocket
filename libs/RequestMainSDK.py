import os
import urllib.request
import threading
import json
from urllib.error import HTTPError

try:
    import pycurl1
    from io import BytesIO
except ImportError:
    pycurl = None


class ConFPub:
    # =======【HTTP客户端设置】===================================
    HTTP_CLIENT = "CURL"  # ("URLLIB", "CURL")
    # HTTP_CLIENT = "URLLIB"  # ("URLLIB", "CURL")
    # =======【证书路径设置】=====================================
    # 证书路径,注意应该填写绝对路径
    # SSLCERT_PATH = os.path.join(settings.BASE_DIR, 'apps/payment/keys/wechat_apiclient_cert.pem')
    # SSLKEY_PATH = os.path.join(settings.BASE_DIR, 'apps/payment/keys/wechat_apiclient_key.pem')
    SSLCERT_PATH = os.path.join("path", 'keys/cert.pem')
    SSLKEY_PATH = os.path.join("path", 'keys/key.pem')

    # =======【url设置】=======================================
    # 支付异步通知url，商户根据实际开发过程设定
    GetUser_URL = "http://www.hfyt365.com:8000/user/"


class Singleton:
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    impl = cls.confingure() if hasattr(cls, "confingure") else cls
                    instance = super(Singleton, cls).__new__(impl, *args, **kwargs)
                    if not isinstance(instance, cls):
                        instance.__init__(*args, **kwargs)
                    cls._instance = instance
        return cls._instance


class UrllibClient:
    """使用urllib2发送请求"""

    def get(self, url, headers: dict, second=30):
        return self.post_json(None, url, headers, second)

    def post_json(self, json, url, headers: dict, second=30):
        if headers:
            if json:
                req = urllib.request.Request(url=url, headers=headers, data=json.encode())
            else:
                req = urllib.request.Request(url=url, headers=headers,)
        else:
            if json:
                req = urllib.request.Request(url=url, data=json.encode())
        try:
            date = urllib.request.urlopen(req, timeout=second).read()
        except HTTPError:
            return "{}"
        return date

    def post_json_ssl(self, json, url, headers=None, second=30):
        raise TypeError("please use CurlClient")


class CurlClient:
    def __init__(self):
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYHOST, False)
        self.curl.setopt(pycurl.SSL_VERIFYPEER, False)
        # 设置不输出header
        self.curl.setopt(pycurl.HEADER, False)

    def get(self, url, headers=None, second=30):
        return self.post_json_ssl(None, url, headers=headers, second=second, cert=False, post=False)

    def post_json(self, json, url, headers=None, second=30):
        return self.post_json_ssl(json, url, headers=headers, second=second, cert=False, post=True)

    def post_json_ssl(self, json, url, second=30, headers=None, cert=True, post=True):
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.TIMEOUT, second)
        if headers:
            header = ["{}:{}".format(k, v) for k, v in headers.items()]
            self.curl.setopt(pycurl.HTTPHEADER, header)
        # 设置证书
        # 使用证书：cert 与 key 分别属于两个.pem文件
        # 默认格式为PEM，可以注释
        if cert:
            self.curl.setopt(pycurl.SSLKEYTYPE, "PEM")
            self.curl.setopt(pycurl.SSLKEY, ConFPub.SSLKEY_PATH)
            self.curl.setopt(pycurl.SSLCERTTYPE, 'PEM')
            self.curl.setopt(pycurl.SSLCERT, ConFPub.SSLCERT_PATH)
        if post:
            self.curl.setopt(pycurl.PORT, True)
            self.curl.setopt(pycurl.POSTFIELDS, json)
        buff = BytesIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buff.write)
        self.curl.perform()
        return buff.getvalue()


class HttpClient(Singleton):
    @classmethod
    def confingure(cls):
        if pycurl is not None and ConFPub.HTTP_CLIENT != "URLLIB":
            return CurlClient
        else:
            return UrllibClient


class CommonUtilPub:
    """所有接口基类"""

    def get(self, url, headers=None, second=30):
        return HttpClient().get(url, headers, second=second)

    def post_json(self, json, url, headers=None, second=30):
        """以POST方式提交json到对应接口的url"""
        return HttpClient().post_json(json, url, headers=None, second=second)

    def post_json_ssl_curl(self, json, url, headers=None, second=30):
        return HttpClient().post_json_ssl(json, url, headers, second=second)

    def bytes_to_odj(self, data):
        if isinstance(data, bytes):
            data = data.decode()
        return json.loads(data)


class GetUserPub(CommonUtilPub):

    def get_user(self, token: str) -> dict:
        """

        :param token:
        :return:
        """
        header = {
            "Authorization": "JWT " + token
        }
        req = self.get(ConFPub.GetUser_URL, header)
        user = self.bytes_to_odj(req)
        if user.get("id") and user.get("username"):
            return user
        else:
            return


if __name__ == '__main__':
    cli = GetUserPub()

    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ilx1NmQ0Ylx1OGJkNVx1NzUyOFx1NjIzNyIsInVzZXJfaWQiOjIyNywiZW1haWwiOiI3OTQyNjc3MDFAcXEuY29tIiwiZXhwIjoxNTkxMTEyNjIxfQ.uXXnVfniI8BdYqFRk0d3-teIdbszxcSUJkaTp84sqkU"
    token = "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Inl1bW9lcjIyIiwidXNlcl9pZCI6MjI2LCJlbWFpbCI6IjEzMDA4NDUyMzRAcXEuY29tIiwiZXhwIjoxNTkwNzg5NDUyfQ.UTaa0myKouNRnw9FFvQrBWIL0GCNW4F9Wjr9LXzuJRE"
    header = {
        "Authorization": "JWT " + token
    }
    a = cli.get_user(token)
    # a = cli.bytes_to_odj(a)
    print(a)