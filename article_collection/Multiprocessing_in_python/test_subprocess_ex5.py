#!/bin/env python
# example of a mutual exclusion (mutex) lock for processes
from datetime import datetime
from time import sleep
from random import random
from multiprocessing import Process
from multiprocessing import Lock


# work function
def task_with_lock(lock, identifier, value):
  # acquire the lock
  with lock:
    print(f'>process {identifier} got the lock, sleeping for {value:.03f}s')
    sleep(value)


def task_ignore_lock(lock, identifier, value):
  # acquire the lock
  print(f'>process {identifier} got the lock, sleeping for {value:.03f}s')
  sleep(value)


# entry point
if __name__ == '__main__':
  # create the shared lock
  lock = Lock()
  # create a number of processes with different sleep times
  random_numbers = [random() for i in range(10)]
  random_number_sum = sum(random_numbers)
  processes = [Process(target=task_ignore_lock, args=(lock, i, random_numbers[i])) for i in range(10)]
  # start the processes
  for process in processes:
    process.start()

  # wait for all processes to finish
  start_time = datetime.now()
  for process in processes:
    process.join()

  time_diff = datetime.now() - start_time
  print(f'Done in {time_diff}  (random nubmer sum={random_number_sum:.03f})!')
