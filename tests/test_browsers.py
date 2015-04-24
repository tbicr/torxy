import pytest

from tests import _get_ip, USER_AGENT, RESOLUTION

from torxy import Tor
from torxy.browsers import get_browser
from torxy.browsers.dummy import DummyBrowser
from torxy.browsers.firefox import FirefoxBrowser
from torxy.browsers.phantom import PhantomBrowser
from torxy.exceptions import BrowserNotFound


def test_firefox():
    with Tor('127.0.0.1', 9052, 9053, '/tmp/tor_instance_9052') as tor:
        browser = tor.get_browser('firefox', user_agent=USER_AGENT, window_size=RESOLUTION)
        assert isinstance(browser, FirefoxBrowser)
        ip = browser.get_ip()
        assert ip != _get_ip()
        tor.ensure_new_tor_identity()
        browser = tor.get_browser('firefox', user_agent=USER_AGENT, window_size=RESOLUTION)
        assert browser.get_ip() != ip


def test_phantom():
    with Tor('127.0.0.1', 9052, 9053, '/tmp/tor_instance_9052') as tor:
        browser = tor.get_browser('phantom', user_agent=USER_AGENT, window_size=RESOLUTION)
        assert isinstance(browser, PhantomBrowser)
        ip = browser.get_ip()
        assert ip != _get_ip()
        tor.ensure_new_tor_identity()
        browser = tor.get_browser('phantom', user_agent=USER_AGENT, window_size=RESOLUTION)
        assert browser.get_ip() != ip


def test_dummy():
    with Tor('127.0.0.1', 9052, 9053, '/tmp/tor_instance_9052') as tor:
        browser = tor.get_browser(None, user_agent=USER_AGENT)
        assert isinstance(browser, DummyBrowser)
        ip = browser.get_ip()
        assert ip != _get_ip()
        tor.ensure_new_tor_identity()
        browser = tor.get_browser(None, user_agent=USER_AGENT)
        assert browser.get_ip() != ip


def test_unknown():
    with pytest.raises(BrowserNotFound):
        get_browser('unknown')
