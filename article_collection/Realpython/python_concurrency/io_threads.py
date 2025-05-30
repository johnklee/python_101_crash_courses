import constants
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor


SITES = constants.SITES


@constants.timer_decorator
def download_all_sites(sites=SITES):
  thread_local = threading.local()

  def get_session_for_thread():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

  def download_site(url):
    session = get_session_for_thread()
    with session.get(url) as response:
        print(f"Read {len(response.content)} bytes from {url}")

  print(f'sites: {sites}')
  with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(download_site, sites)


if __name__ == "__main__":
  download_all_sites()
