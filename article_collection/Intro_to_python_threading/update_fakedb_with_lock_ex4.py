# This script will block.
from constants import Color, ColorOptions
import concurrent.futures
import logging
import threading
import time


format = "%(asctime)s: %(message)s"
logging.basicConfig(
    format=format, level=logging.DEBUG, datefmt="%H:%M:%S")


class FakeDatabase:
  def __init__(self):
    self.value = 0
    self._lock = threading.RLock()

  def locked_sync(self, name):
    with self._lock:
      logging.info('Synchronizing the memory into persistent store...')

  def update(self, name):
    logging.info(ColorOptions[name] + "Thread %s: starting update" + Color.END, name)
    with self._lock:
      logging.debug(ColorOptions[name] + "Thread %s has lock" + Color.END, name)
      local_copy = self.value
      local_copy += 1
      time.sleep(0.1)
      self.value = local_copy
      self.locked_sync(name)
      logging.debug(ColorOptions[name] + "Thread %s about to release lock" + Color.END, name)

    logging.info(Color.BOLD + ColorOptions[name] + "Thread %s: === finishing update ===" + Color.END, name)


if __name__ == "__main__":
  database = FakeDatabase()
  logging.info("Testing update. Starting value is %d.", database.value)
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    for index in range(2):
      executor.submit(database.update, index)

    # executor.shutdown(wait=True, cancel_futures=True)

  logging.info("Testing update. Ending value is %d.", database.value)
