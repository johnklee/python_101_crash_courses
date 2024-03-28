import logging
import concurrent.futures
import time


class Color:
  """Terminal Color information."""

  # Color
  PURPLE = '\033[95m'
  CYAN = '\033[96m'
  DARKCYAN = '\033[36m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  DARK_RED = '\033[31m'

  # Set
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  END = '\033[0m'
  BLINK_SLOW = '\033[5m'

  # Combination
  BLINK_BOLD_RED_SLOW = BOLD + RED + BLINK_SLOW


color_options = [Color.BLUE, Color.YELLOW, Color.GREEN]

def thread_function(name):
  color = color_options[name]
  logging.info(
      Color.BOLD + color + "Thread %s: !!! starting !!!" + Color.END, name)
  for i in range(5):
    logging.info(color + 'Thread %s: Handling task %s...' + Color.END, name, i)

  logging.info(
      Color.BOLD + Color.DARK_RED +
      "=== Thread %s: finishing ===" + Color.END, name)


if __name__ == "__main__":
  format = "%(asctime)s: %(message)s"
  logging.basicConfig(format=format, level=logging.INFO,
                      datefmt="%H:%M:%S")

  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(thread_function, range(3))
