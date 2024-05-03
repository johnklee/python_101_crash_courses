#!/bin/env python
import datetime
import math
import os
import time
import threading



def cpu_heavy_job(name: str):
  print(f'Start thread-{name} with pid={os.getpid()}')
  ans = 0
  for i in range(50000000):
    math.sqrt(64*64*64*64*64)


if __name__ == '__main__':
  print(f'Main thread with pid: {os.getpid()}')
  start_time = datetime.datetime.now()
  threads = []
  for thd_num in range(1, 5):
    for i in range(thd_num):
      thd = threading.Thread(target=cpu_heavy_job, args=(i,))

      threads.append(thd)
      thd.start()

    for thd in threads:
      thd.join()

    time_diff = datetime.datetime.now() - start_time
    print(f'===> Thd number {thd_num} took {time_diff}')

  print('Done!')
