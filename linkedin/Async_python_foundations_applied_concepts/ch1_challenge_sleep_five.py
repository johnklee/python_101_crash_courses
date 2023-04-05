#!/bin/env python
import asyncio
from datetime import datetime
import click


async def sleep_five():
  print(f'Starting 5s sleep...')
  await asyncio.sleep(5)
  print(f'Finished 5s sleep!')
  return 5


async def sleep_three_then_five():
  print(f'Starting 3s sleep...')
  await asyncio.sleep(3)
  print(f'Finished 3s sleep!')
  results = await sleep_five()
  return 3 + results


async def main():
  await asyncio.gather(
      sleep_three_then_five(), sleep_five())


start = datetime.now()
asyncio.run(main())

click.secho(
    f'{datetime.now() - start}', bold=True, bg='blue', fg='white')
