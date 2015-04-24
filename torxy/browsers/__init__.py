import torxy.exceptions


class BrowserMixin(object):

    _service = 'http://wtfismyip.com/text'

    def get_ip(self):
        self.get(self._service)
        result = self.find_element_by_tag_name('body').text.strip()
        return result


def get_browser(name=None, proxy_address='127.0.0.1', proxy_port=9050, **kwargs):
    if name is None:
        from torxy.browsers.dummy import DummyBrowser
        return DummyBrowser(proxy_address, proxy_port, **kwargs)

    if name == 'firefox':
        from torxy.browsers.firefox import FirefoxBrowser
        return FirefoxBrowser(proxy_address, proxy_port, **kwargs)

    if name == 'phantom':
        from torxy.browsers.phantom import PhantomBrowser
        return PhantomBrowser(proxy_address, proxy_port, **kwargs)

    raise torxy.exceptions.BrowserNotFound()
