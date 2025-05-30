#!/usr/bin/env python
import asyncio
import constants
import time


async def fib(n):
  return n if n < 2 else await fib(n - 2) + await fib(n - 1)

async def async_main():
  tasks = [fib(35) for _ in range(20)]
  await asyncio.gather(*tasks, return_exceptions=True)


@constants.timer_decorator
def main():
  asyncio.run(async_main())


if __name__ == "__main__":
  main()
