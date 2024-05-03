#!/bin/env python
# example of a reentrant lock for processes
from time import sleep
from random import random
from multiprocessing import Process
from multiprocessing import Lock
from multiprocessing import RLock


# reporting function
def report(lock, identifier):
  # acquire the lock
  with lock:
    print(f'>process {identifier} done')


# work function
def task(lock, identifier, value):
  # acquire the lock
  with lock:
    print(f'>process {identifier} sleeping for {value}')
    sleep(value)
    # report
    report(lock, identifier)


# entry point
if __name__ == '__main__':
  # create a shared reentrant lock
  lock = RLock()
  # lock = Lock()

  # create processes
  processes = [Process(target=task, args=(lock, i, random())) for i in range(10)]

  # start child processes
  for process in processes:
    process.start()

  # wait for child processes to finish
  for process in processes:
    process.join()
