import glob
import logging

import selenium.webdriver

import torxy.browsers


logger = logging.getLogger()


class PhantomBrowser(selenium.webdriver.PhantomJS, torxy.browsers.BrowserMixin):

    def __init__(self, proxy_address='127.0.0.1', proxy_port=9050, *,
                 binary=None, user_agent=None, window_size=None):
        logger.info('Starting phantom browser')
        described_capabilities = dict(selenium.webdriver.DesiredCapabilities.PHANTOMJS)
        if user_agent:
            described_capabilities['phantomjs.page.settings.userAgent'] = user_agent

        super(PhantomBrowser, self).__init__(
            binary or glob.glob('phantomjs*/bin/phantomjs')[0],
            desired_capabilities=described_capabilities,
            service_args=[
                '--proxy={}:{}'.format(proxy_address, proxy_port),
                '--proxy-type=socks5',
            ])
        if window_size:
            self.set_window_size(*window_size)
        logger.info('Started phantom browser')
