#!/usr/bin/env python
import constants
import requests


SITES = constants.SITES


@constants.timer_decorator
def download_all_sites(sites=SITES):
  with requests.Session() as session:
    for url in sites:
      with session.get(url) as response:
        print(f"Read {len(response.content)} bytes from {url}")


if __name__ == '__main__':
  download_all_sites()
