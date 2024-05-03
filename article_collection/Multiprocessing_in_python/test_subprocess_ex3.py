#!/bin/env python
import os

from time import sleep
from multiprocessing import Process


STOP_SIGNAL = os.path.join(os.getcwd(), 'STOP')


class MyProcess(Process):

  def __init__(self, name: str):
    super().__init__()
    self.name = name

  def run(self):
    print(f'Subprocess of "{self.name}" with pid: {os.getpid()}')
    print('Wait for STOP signal...')
    while not os.path.isfile(STOP_SIGNAL):
      sleep(1)

    print(f'Exit subprocess({os.getpid()})')


if __name__ == '__main__':
  print(f'Main process with pid: {os.getpid()}')

  # 1) Create processes
  my_process1 = MyProcess('John')
  my_process2 = MyProcess('Mary')

  # 2) Start the processes
  my_process1.start()
  my_process2.start()

  # 3) Join the processes
  my_process1.join()
  my_process2.join()

  os.remove(STOP_SIGNAL)

  print('Bye!')

