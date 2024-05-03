#!/bin/env python
# example of running a function with arguments in another process
import os

from time import sleep
from multiprocessing import Process


# a custom function that blocks for a moment
def task2(sleep_time, message):
  print(f'Subprocess with PID: {os.getpid()}')
  # block for a moment
  sleep(sleep_time)
  # display a message
  print(message)
  print(f'Exit from {os.getpid()}')


# entry point
if __name__ == '__main__':
  print(f'Main process with PID: {os.getpid()}')

  # create a process
  process1 = Process(target=task2, args=(1.5, 'New message from another process'))
  process2 = Process(target=task2, args=(2, 'New message from another process'))

  # run the process
  process1.start()
  process2.start()

  # wait for the process to finish
  print('Waiting for the process...')
  process1.join()
  process2.join()

  print('Bye!')
