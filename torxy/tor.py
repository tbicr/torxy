import logging
import subprocess
import time
import multiprocessing
import shutil

import stem
import stem.control

import torxy.browsers
import torxy.exceptions
import torxy.utils


logger = logging.getLogger()


class Tor(object):

    def __init__(self, address, port, control_port, data_directory, wait_start=0, wait_check=0):
        self.address = address
        self.port = port
        self.control_port = control_port
        self.data_directory = data_directory
        self.password = torxy.utils.generate_password()
        self._browsers = []
        self.start(wait_start, wait_check)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def password_hash(self):
        out, err = subprocess.Popen(['tor', '--quiet', '--hash-password', self.password],
                                    stdout=subprocess.PIPE).communicate()
        return out.decode().strip()

    def start(self, wait_start=0, wait_check=0):
        logger.info('Starting tor instance')
        self.subprocess = subprocess.Popen([
            'tor',
             '--SocksPort', str(self.port),
             '--ControlPort', str(self.control_port),
             '--DataDirectory', self.data_directory,
             '--CookieAuthentication', '0',
             '--HashedControlPassword', '',
        ])
        if wait_start:
            time.sleep(wait_start)
        if wait_check:
            try:
                self.get_browser().get_ip()
            except:
                logger.warning('Get error when check tor connection', exc_info=True)
            time.sleep(wait_check)
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

        ip = new_ip = browser.get_ip()
        browser.quit()
        while attempts > 0:
            self.new_tor_identity()
            while checks > 0:
                time.sleep(sleep)
                browser = self.get_browser(browser_name)
                try:
                    new_ip = browser.get_ip()
                except Exception:
                    logger.warning('Can\'t get ip', exc_info=True)
                browser.quit()
                if ip != new_ip:
                    logger.info('Got new tor identity: %s', new_ip)
                    return
                checks -= 1
            attempts -= 1
        raise torxy.exceptions.IdentityNotChanged('Can\'t get new tor identity')


def process(handler, data, port=9052, control_port=9053, data_directory='/tmp/tor_instance_{}',
            step=2, wait_start=0, wait_check=0, wait_before_next=0, Process=multiprocessing.Process):
    processes = []
    for index, args in enumerate(data):
        def wrapper(*args, **kwargs):
            address, port, control_port, data_directory, wait_start, wait_check, *args = args
            while True:
                try:
                    with Tor(address, port, control_port, data_directory,
                             wait_start=wait_start, wait_check=wait_check) as tor:
                        handler(tor, *args, **kwargs)
                except torxy.exceptions.RestartTor:
                    continue
                break

        p = Process(target=wrapper, args=(
                '127.0.0.1',
                port + index * step,
                control_port + index * step,
                data_directory.format(port + index * step),
                wait_start,
                wait_check,
            ) + args)
        p.start()
        processes.append(p)
        if wait_before_next:
            time.sleep(wait_before_next)
    for p in processes:
        p.join()
