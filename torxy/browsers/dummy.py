import logging
import urllib.request

import socks
import sockshandler

import torxy.browsers
import torxy.exceptions


logger = logging.getLogger()


class DummyBrowserClosed(torxy.exceptions.BaseException):

    pass


class DummyBrowser(torxy.browsers.BrowserMixin):

    def __init__(self, proxy_address='127.0.0.1', proxy_port=9050, *,
                 user_agent=None):
        logger.info('Starting dummy browser')
        handler = sockshandler.SocksiPyHandler(socks.SOCKS5, proxy_address, proxy_port)
        self._opener = urllib.request.build_opener(handler)
        self._user_agent = user_agent
        self._open = True
        logger.info('Started dummy browser')

    def _check_open(self):
        if not self._open:
            raise DummyBrowserClosed()

    def get(self, url):
        self._check_open()
        request = urllib.request.Request(url)
        if self._user_agent:
            request.add_header('User-Agent', self._user_agent)
        response = self._opener.open(request)
        self._page_source = response.read()
        self._current_url = response.url
        response.close()

    @property
    def current_url(self):
        self._check_open()
        return self._current_url

    @property
    def page_source(self):
        self._check_open()
        return self._page_source

    def quit(self):
        self._open = False

    def get_ip(self):
        self._check_open()
        self.get('http://wtfismyip.com/text')
        result = self.page_source.decode().strip()
        return result
