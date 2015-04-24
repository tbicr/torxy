import functools
import urllib.request

from torxy.browsers import BrowserMixin


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'
RESOLUTION = (800, 600)


@functools.lru_cache()
def _get_ip():
    return urllib.request.urlopen(BrowserMixin._service).read().decode().strip()
