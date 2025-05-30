import constants

import atexit
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor

import requests


SITES = constants.SITES
session: requests.Session | None = None


@constants.timer_decorator
def main():
  download_all_sites()


def download_all_sites(sites=SITES):
  with ProcessPoolExecutor(initializer=init_process) as executor:
    executor.map(download_site, sites)


def download_site(url):
  global session
  print(f'Session: {session}')
  with session.get(url) as response:
    name = multiprocessing.current_process().name
    print(f"{name}:Read {len(response.content)} bytes from {url}")


def init_process():
  global session
  session = requests.Session()
  atexit.register(session.close)
  print('Initialized process!')


if __name__ == "__main__":
  main()
