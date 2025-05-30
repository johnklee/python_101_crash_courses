#!/usr/bin/env python
import constants
import time
from concurrent.futures import ProcessPoolExecutor


def fib(n):
  return n if n < 2 else fib(n - 2) + fib(n - 1)


@constants.timer_decorator
def main():
  with ProcessPoolExecutor() as executor:
    executor.map(fib, [35] * 20)


if __name__ == "__main__":
    main()
