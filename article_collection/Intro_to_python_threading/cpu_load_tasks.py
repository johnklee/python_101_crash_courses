from constants import Color, ColorOptions
import copy
import concurrent.futures
from datetime import datetime
import math
import logging
import matplotlib.pyplot as plt
import threading
import time


format = "%(asctime)s: %(message)s"
logging.basicConfig(
    format=format, level=logging.DEBUG, datefmt="%H:%M:%S")


def generate_cpu_load(interval=3, utilization=100):
    "Generate a utilization % for a duration of interval seconds"
    start_time = time.time()
    print("About to do some arithmetic")
    for i in range(0,int(interval)):
        while time.time()-start_time < utilization/100.0:
            a = math.sqrt(64*64*64*64*64)
        time.sleep( 1 - utilization/ 100.0)
        start_time += 1


CPU_LOAD_TASKS = [generate_cpu_load] * 50


def thread_body(name, tasks):
  logging.info(
      ColorOptions[name] + 'Thread=%s: Input task size=%s' + Color.END, name, len(tasks))
  while tasks:
    task = tasks.pop(0)
    logging.info(
        ColorOptions[name] + 'Thread-%s: Start executing task' + Color.END, name)
    task()
  logging.info(
      ColorOptions[name] + 'Thread-%s exit!' + Color.END, name)


thread_num_2_process_time = {}
for thread_num in range(5, 11):
    start_time = datetime.now()
    tasks = copy.copy(CPU_LOAD_TASKS)
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
      executor.map(
          lambda args: thread_body(*args), ((name, tasks) for name in range(thread_num)))

    time_diff = datetime.now() - start_time
    thread_num_2_process_time[thread_num] = time_diff.total_seconds()
    print(f'Thread number={thread_num} spent {time_diff.total_seconds():.02f}s\n\n')
