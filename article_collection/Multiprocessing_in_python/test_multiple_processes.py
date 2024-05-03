#!/bin/env python
import datetime
import math
import multiprocessing
from multiprocessing import Process
import os
import time



def cpu_heavy_job(name: str):
  print(f'Start thread-{name} with pid={os.getpid()}')
  ans = 0
  for i in range(50000000):
    math.sqrt(64*64*64*64*64)


if __name__ == '__main__':
  print(f'Main thread with pid: {os.getpid()}')

  for proc_count in range(1, 5):
    start_time = datetime.datetime.now()
    processes = []
    for i in range(proc_count):
      poc = Process(target=cpu_heavy_job, args=(i,))

      processes.append(poc)
      poc.start()

    for poc in processes:
      poc.join()

    time_diff = datetime.datetime.now() - start_time
    print(f'===> Process {proc_count} took {time_diff}!')
