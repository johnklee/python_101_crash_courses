#!/bin/env python
# example of extending the Process class and adding shared attributes
import os
from time import sleep
from multiprocessing import Process
from multiprocessing import Value


# custom process class
class CustomProcess(Process):
  # override the constructor
  def __init__(self, name: str):
    # execute the base constructor
    Process.__init__(self)
    self.name = name

    # initialize integer attribute
    self.data = Value('i', 0)

  @property
  def identity(self):
    return f'{self.name}:{os.getpid()}'

  # override the run function
  def run(self):
    # block for a moment
    sleep(1)
    # store the data variable
    self.data.value = 99
    # report stored value
    print(f'{self.identity} > Child stored: {self.data.value}')


# entry point
if __name__ == '__main__':
  print(f'Main process with pid: {os.getpid()}')

  # create the process
  process = CustomProcess('John')
  print(f'Parent with process.data.value: {process.data.value}')

  # start the process
  process.start()

  # wait for the process to finish
  print('Waiting for the child process to finish')
  # block until child process is terminated
  process.join()

  # report the process attribute
  print(f'Parent got: {process.data.value}')
