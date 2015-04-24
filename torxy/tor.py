import logging
import subprocess
import time
import shutil
import multiprocessing

import stem
import stem.control

import torxy.browsers
import torxy.exceptions
from torxy.utils import generate_password


logger = logging.getLogger()


class Tor(object):

    def __init__(self, address, port, control_port, data_directory):
        self.address = address
        self.port = port
        self.control_port = control_port
        self.data_directory = data_directory
        self.password = generate_password()
        self._browsers = []
        self.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def password_hash(self):
        out, err = subprocess.Popen(['tor', '--quiet', '--hash-password', self.password],
                                    stdout=subprocess.PIPE).communicate()
        return out.decode().strip()

    def start(self, sleep=1):
        logger.info('Starting tor instance')
        self.subprocess = subprocess.Popen([
            'tor',
             '--SocksPort', str(self.port),
             '--ControlPort', str(self.control_port),
             '--DataDirectory', self.data_directory,
             '--CookieAuthentication', '0',
             '--HashedControlPassword', '',
        ])
        time.sleep(sleep)
        logger.info('Started tor instance')

    def close(self):
        logger.info('Closing tor instance')
        self.quit_browsers()
        self.subprocess.terminate()
        shutil.rmtree(self.data_directory, ignore_errors=True)
        logger.info('Closed tor instance')

    def get_browser(self, browser_name=None, **kwargs):
        browser = torxy.browsers.get_browser(browser_name, self.address, self.port, **kwargs)
        self._browsers.append(browser)
        return browser

    def quit_browsers(self):
        for browser in self._browsers:
            try:
                browser.quit()
            except:
                pass
        self._browsers.clear()

    def new_tor_identity(self):
        with stem.control.Controller.from_port(self.address, self.control_port) as controller:
            controller.authenticate()
            controller.signal(stem.Signal.NEWNYM)

    def ensure_new_tor_identity(self, attempts=3, checks=5, sleep=1, browser_name=None):
        logger.info('Getting new tor identity')
        self.quit_browsers()
        browser = self.get_browser(browser_name)

        ip = browser.get_ip()
        browser.quit()
        while attempts > 0:
            self.new_tor_identity()
            while checks > 0:
                time.sleep(sleep)
                browser = self.get_browser(browser_name)
                new_ip = browser.get_ip()
                browser.quit()
                if ip != new_ip:
                    logger.info('Got new tor identity: %s', new_ip)
                    return
                checks -= 1
            attempts -= 1
        raise torxy.exceptions.IdentityNotChanged('Can\'t get new tor identity')


def process(handler, data, port=9052, control_port=9053, data_directory='/tmp/tor_instance_',
            step=2, Process=multiprocessing.Process):
    processes = []
    for index, args in enumerate(data):
        def wrapper(*args, **kwargs):
            address, port, control_port, data_directory, *args = args
            with Tor(address, port, control_port, data_directory) as tor:
                handler(tor, *args, **kwargs)

        p = Process(target=wrapper, args=(
                '127.0.0.1',
                port + index * step,
                control_port + index * step,
                '{}{}'.format(data_directory, port + index * step),
            ) + args)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
