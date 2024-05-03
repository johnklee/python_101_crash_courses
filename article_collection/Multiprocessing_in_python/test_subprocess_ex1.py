#!/bin/env python
import os
from multiprocessing import Process
from time import sleep


STOP_SIGNAL = os.path.join(os.getcwd(), 'STOP')


# a custom function that blocks for a moment
def task():
  # block for a moment
  print(f'Subprocess PID: {os.getpid()}')
  print(f'Current working directory: {os.getcwd()}')
  print('Touch file "STOP" to stop the task...')
  while not os.path.isfile(STOP_SIGNAL):
    sleep(1)

  # display a message
  print('Stopping')


if __name__ == '__main__':
  print(f'Parent process id: {os.getpid()}')
  # create a process
  process1 = Process(target=task)
  process2 = Process(target=task)

  # run the process
  process1.start()
  process2.start()

  # wait for the process to finish
  print('Waiting for the process...')
  process1.join()
  process2.join()

  print('Sub processes are all done!')
  if os.path.isfile(STOP_SIGNAL):
    os.remove(STOP_SIGNAL)

  print('Sleep 5s for main process to quit...')
  sleep(5)
