import concurrent.futures
from constants import Color, ColorOptions
import logging
import random
import threading
import time


format = "%(asctime)s: %(message)s"
logging.basicConfig(
    format=format, level=logging.INFO, datefmt="%H:%M:%S")

logging.getLogger().setLevel(logging.DEBUG)


class Restaurant:
  def __init__(self, capacity: int = 3):
    self.lock = threading.Semaphore(capacity)
    self.guest_count = 0

  def serve(self, guest_id: int):
    with self.lock:
      self.guest_count += 1
      logging.info(
          ColorOptions[guest_id] +
          'Serving guest-%s (guest count=%s)' +
          Color.END, guest_id, self.guest_count)

      time.sleep(random.uniform(0, 1))
      self.guest_count -= 1

    logging.info(
        ColorOptions[guest_id] + 'Guest-%s left!' +
        Color.END, guest_id)


if __name__ == '__main__':
  restaurant = Restaurant()

  guest_number = 6
  with concurrent.futures.ThreadPoolExecutor(max_workers=guest_number) as executor:
    executor.map(restaurant.serve, range(guest_number))

  logging.info('Main: Restaurant has %s guest left!', restaurant.guest_count)
  logging.info('Main: Bye!')
