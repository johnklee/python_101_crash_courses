#!/bin/env python
import constants
import time


@constants.timer_decorator
def main():
  for _ in range(20):
    fib(35)


def fib(n):
  return n if n < 2 else fib(n - 2) + fib(n - 1)


if __name__ == "__main__":
  main()
