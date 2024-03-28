# example of using a barrier
from constants import Color, ColorOptions
from time import sleep
from random import random
from threading import Thread
from threading import Barrier

# target function to prepare some work
def task(barrier, number):
  # generate a unique value
  value = random() * 10
  # block for a moment
  sleep(value)
  # report result
  print(
      ColorOptions[number] + f'Thread {number} done, got: {value}' + Color.END)
  # wait on all other threads to complete
  barrier.wait()
  print(
      ColorOptions[number] + f'Thread {number} exit!' + Color.END)

# create a barrier
barrier = Barrier(2)

# create the worker threads
workers = []
for i in range(6):
    # start a new thread to perform some work
    worker = Thread(target=task, args=(barrier, i))
    worker.start()
    workers.append(worker)

# wait for all threads to finish
print('Main thread waiting on all results...')
for worker in workers:
  worker.join()


# report once all threads are done
print('All threads have their result')
