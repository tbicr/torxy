from multiprocessing.dummy import DummyProcess

from tests import _get_ip

from torxy import process
from torxy.browsers.dummy import DummyBrowser


def test_processes():
    def handler(tor, a, b):
        browser = tor.get_browser()
        assert isinstance(browser, DummyBrowser)
        ip = browser.get_ip()
        assert ip != _get_ip()
        tor.ensure_new_tor_identity()
        browser = tor.get_browser()
        assert browser.get_ip() != ip
        assert a == 1
        assert b == 'test'

    process(handler, [(1, 'test')])
    process(handler, [(1, 'test')], Process=DummyProcess)
