import logging

import selenium.webdriver

import torxy.browsers


logger = logging.getLogger()


class FirefoxBrowser(selenium.webdriver.Firefox, torxy.browsers.BrowserMixin):

    def __init__(self, proxy_address='127.0.0.1', proxy_port=9050, *, binary=None,
                 user_agent=None, window_size=None):
        logger.info('Starting firefox browser')
        profile = selenium.webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference('network.proxy.socks', proxy_address)
        profile.set_preference('network.proxy.socks_port', proxy_port)
        if user_agent:
            profile.set_preference('general.useragent.override', user_agent)

        super(FirefoxBrowser, self).__init__(profile, binary)
        if window_size:
            self.set_window_size(*window_size)
        logger.info('Started firefox browser')
