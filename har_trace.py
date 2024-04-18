import os
import time
import psutil
import pathlib
from datetime import datetime
from pathlib import Path

import browsermobproxy
import browsermobproxy.exceptions
import selenium.webdriver
import selenium.common.exceptions


class HARGenerator():
    # This class is used to interact with BrowserMob Proxy, see here: https://github.com/lightbody/browsermob-proxy
    # Source code for Python API is: https://browsermob-proxy-py.readthedocs.io/en/latest/_modules/browsermobproxy/server.html#Server
    # Please make sure your system has the required Java runtime for the server to run properly.

    def __init__(self, port, log_dir='logs', bin_path='utils/har/browsermob-proxy-2.1.4/bin'):
        self.port = port
        self.terminated = False

        self.bin_path = bin_path
        self.log_dir = log_dir
        self.bmp_log_path = self._set_log_path(self.log_dir, 'bmp')
        self.chrome_driver_log_path = self._set_log_path(
            self.log_dir, 'chromedriver')

        self._start_server()
        self._create_proxy_server()
        self._start_chrome_driver()

    """ Private class functions """

    def _set_log_path(self, parent_path, child_path):
        path = os.path.join(parent_path, child_path)
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        return path

    def _start_server(self):
        try:
            print(f"Setting up server...", end='', flush=True)
            self.server = browsermobproxy.Server(
                path=os.path.join(self.bin_path, 'browsermob-proxy'),
                options={'port': self.port}
            )
            print(f"OK")

            print(f"Starting server...", end='', flush=True)
            self.server.start(options={
                'log_file': f'{datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}.log',
                'log_path': self.bmp_log_path,
                'retry_count': 5
            })
            print(f"OK")

        except browsermobproxy.exceptions.ProxyServerError as err:
            print(f"Error starting server. Please check server logs. Exiting...")
            print(str(err))
            exit(-1)

    def _create_proxy_server(self):
        print(f"Creating proxy server...", end='', flush=True)
        self.proxy = self.server.create_proxy(
            params={"trustAllServers": "true"})
        print(f"OK")

    def _start_chrome_driver(self):
        print(f"Creating Chrome driver...", end='', flush=True)
        self.driver = selenium.webdriver.Chrome(options=self._chrome_options())
        print(f"OK")

    def _chrome_options(self):
        options = selenium.webdriver.ChromeOptions()
        options.add_argument("--proxy-server={}".format(self.proxy.proxy))
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--headless")
        options.add_argument("--no-cache")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--verbose")
        options.add_argument(f"--log-path={self.chrome_driver_log_path}")

        return options

    """ Public class functions """

    def get_har(self, hostname, append_https=False):
        self.proxy.new_har(hostname)
        self.driver.set_page_load_timeout(60)

        try:
            if append_https:
                assert (not hostname.startswith('https://'))
                hostname = f'https://{hostname}'
            self.driver.get(hostname)

        except selenium.common.exceptions.TimeoutException as err:
            print(f'Timeout from renderer for {hostname}. Skipping...', 'FAIL')

        except selenium.common.exceptions.WebDriverException as err:
            print(
                f'ERR_TUNNEL_CONNECTION_FAILED from renderer for {hostname}. Skipping...', 'FAIL')

        except Exception as err:
            print(f'Unexpected error: {err}.\n Skipping...', 'FAIL')

        time.sleep(1)

        return self.proxy.har

    def parse_har_and_get_resources(self, har):
        entries = har.get('log', {}).get('entries', [])
        for entry in entries:
            resource = entry.get('request', {}).get('url', '')
            yield resource

    def terminate(self):
        try:
            """
            BrowserMobProxy starts a process (parent process), which starts another process running the proxy server (child process)
            Calling self.server.stop() only stops the parent process but not the child process, which becomes a zombie process when the program ends
            """

            for child in psutil.Process(self.server.process.pid).children(recursive=True):
                child.kill()

            self.server.stop()
            self.driver.quit()

            """ This is to prevent "ImportError: sys.meta_path is None, Python is likely shutting down" from Selenium, see here: https://stackoverflow.com/questions/41480148/importerror-sys-meta-path-is-none-python-is-likely-shutting-down """
            time.sleep(1)
            self.terminated = True

        except ImportError:
            """ Ignore "ImportError: sys.meta_path is None, Python is likely shutting down" """
            pass

    def __del__(self):
        if not self.terminated: self.terminate()


if __name__ == '__main__':
    import json

    har_gen = HARGenerator(port=8080)

    hostname = "2023.brainonline.com"
    har_dict = har_gen.get_har(hostname)

    with open('har.json', 'w') as f:
        json.dump(har_dict, f)

    har_gen.terminate()