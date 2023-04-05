import concurrent.futures
import logging
import time


format = "%(asctime)s: %(message)s"
logging.basicConfig(
    format=format, level=logging.INFO, datefmt="%H:%M:%S")


class FakeDatabase:
    def __init__(self):
        self.value = 0

    def update(self, name):
        logging.info("Thread %s: starting update", name)
        local_copy = self.value
        local_copy += 1
        time.sleep(0.1)
        self.value = local_copy
        logging.info("Thread %s: finishing update", name)


if __name__ == "__main__":
    database = FakeDatabase()
    logging.info("Testing update. Starting value is %d.", database.value)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for index in range(2):
            executor.submit(database.update, index)

        executor.shutdown(wait=True, cancel_futures=True)

    logging.info("Testing update. Ending value is %d.", database.value)
