import asyncio
import logging
import time


SITES = (
        "https://www.jython.org",
        "http://olympus.realpython.org/dice",
) * 50


def timer_decorator(func):
  def wrap():
    start_time = time.perf_counter()
    resp = func()
    duration = time.perf_counter() - start_time
    print(f'Execution time: {duration:.02f}s')
    return resp

  return wrap


def async_timer_decorator(func):
  async def wrap():
    start_time = time.perf_counter()
    resp = await func()
    duration = time.perf_counter() - start_time
    print(f'Execution time: {duration:.02f}s')

    return resp

  return wrap
