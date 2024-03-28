import logging
import threading
import time

format = "%(asctime)s: %(message)s"
logging.basicConfig(
    format=format, level=logging.INFO, datefmt="%H:%M:%S")


def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(5)
    logging.info("Thread %s: finishing (You won't see this line)", name)



if __name__ == '__main__':
  logging.info("Main    : before creating thread")

  x = threading.Thread(target=thread_function, args=("John's daemon",), daemon=True)
  # x = threading.Thread(target=thread_function, args=(1,))
  logging.info("Main    : before running thread")

  # Starting the thread
  x.start()

  logging.info("Main    : wait for the thread to finish")
  logging.info("Main    : all done")
  # x.join()
