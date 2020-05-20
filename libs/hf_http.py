import urllib.request
import threading
import pycurl

try:
    import pycurl
    from io import BytesIO
except ImportError:
    pycurl = None


class ConFPub:
    # =======【HTTP客户端设置】===================================
    HTTP_CLIENT = "CURL"  # ("URLLIB", "CURL")

    SSLKEY_PATH = ''

    SSLCERT_PATH = ''


class Singleton:
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    impl = cls.configure() if hasattr(cls, "configure") else cls
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
            req = urllib.request.Request(url=url, headers=headers, data=json.encode())
        else:
            req = urllib.request.Request(url=url, data=json.encode())
        date = urllib.request.urlopen(req, timeout=second).reade()
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
            self.curl.setopt(pycurl.WRITEHEADER, headers)
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

    def get(self, url, headers, second=30):
        return HttpClient().get(url, headers, second=second)

    def post_json(self, json, url, headers, second=30):
        """以POST方式提交json到对应接口的url"""
        return HttpClient().post_json(json, url, headers, second=second)

    def post_json_ssl_curl(self, json, url, header, second=30):
        return HttpClient().post_json_ssl(json, url, header, second=second)
