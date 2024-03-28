import logging
import threading
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


def thread_function(name, color):
    logging.info(Color.BOLD + color + "Thread %s: !!! starting !!!" + Color.END, name)
    for i in range(10):
      logging.info(color + 'Thread %s: Handling task %s...' + Color.END, name, i)
    logging.info("Thread %s: finishing", name)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    color_options = [Color.BLUE, Color.YELLOW, Color.GREEN]
    threads = list()
    for index in range(3):
        logging.info("Main    : create and start thread %d.", index)
        x = threading.Thread(
            target=thread_function,
            args=(index, color_options[index]))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : start joining thread %d.", index)
        thread.join()
        logging.info(
            Color.BOLD + Color.DARK_RED +
            "Main    : === thread %d done ===" +
            Color.END, index)
