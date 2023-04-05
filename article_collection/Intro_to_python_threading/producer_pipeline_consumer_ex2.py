import concurrent.futures
import logging
import queue
import random
import threading
import time


format = "%(asctime)s: %(message)s"
logging.basicConfig(
    format=format, level=logging.INFO, datefmt="%H:%M:%S")

logging.getLogger().setLevel(logging.DEBUG)
SENTINEL = object()


def producer(pipeline, event):
    """Pretend we're getting a message from the network."""
    sent_message_count = 0
    while not event.is_set():
        message = random.randint(1, 101)
        logging.info("Producer got message: %s", message)
        pipeline.put(message)
        sent_message_count += 1
        time.sleep(0.4)

    logging.info("Producer received EXIT event. Exiting (%d)", sent_message_count)


def consumer(pipeline, event):
    """Pretend we're saving a number in the database."""
    received_message_count = 0
    while not event.is_set() or not pipeline.empty():
        try:
          message = pipeline.get(False)
        except Exception as ex:
          logging.info('Wait 1s for empty queue...%s', ex)
          time.sleep(1)
          continue

        received_message_count += 1
        logging.info(
            "Consumer storing message: %s  (queue size=%s)",
            message,
            pipeline.qsize(),
        )

    logging.info("Consumer received EXIT event. Exiting (%d)", received_message_count)


if __name__ == "__main__":
    event = threading.Event()
    pipeline = queue.Queue(maxsize=10)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer, pipeline, event)
        executor.submit(consumer, pipeline, event)

        time.sleep(3)
        logging.info("Main: about to set event")
        event.set()
        executor.shutdown(wait=True, cancel_futures=True)
