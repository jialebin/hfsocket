from tornado.web import url as ueb_url
from importlib import import_module
from typing import Pattern


class Url:
    def __init__(self, pattern: [str, Pattern], handler_class, kwarges=None, name=None):
        self.patter = pattern
        self.handler_class = handler_class
        self.kwargs = kwarges
        self.name = name


url = Url


def include(module):
    res = import_module('handlers.' + module)
    urls = getattr(res, 'urls', res)
    return urls


def url_wrapper(urls: list):
    wrapper_list = []
    for url in urls:
        path, handles = url
        for handle in handles:
            if isinstance(handles, (tuple, list)):
                pattern, handle_class = handle
                wrap = ("{0}{1}".format(path, pattern), handle_class)
                wrapper_list.append(wrap)
            else:
                wrapper_list.append((path, handles))
    return wrapper_list


urls = url_wrapper([
    ("", include('main.urls'))
])
