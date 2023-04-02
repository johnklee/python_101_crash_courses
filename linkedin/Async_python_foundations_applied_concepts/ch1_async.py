import asyncio
from datetime import datetime
import click


async def sleep_and_print(wait_time_sec: int):
    print(f'Starting {wait_time_sec}s sleep...')
    await asyncio.sleep(wait_time_sec)
    print(f'Finished {wait_time_sec}s sleep!')
    return wait_time_sec


async def main():
    results = await asyncio.gather(
        sleep_and_print(3), sleep_and_print(6))


start = datetime.now()

asyncio.run(main())

click.secho(
    f'{datetime.now() - start}',
    bold=True, bg="blue", fg="white")
