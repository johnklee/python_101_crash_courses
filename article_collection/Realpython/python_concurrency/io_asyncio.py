import constants

import asyncio
import time

import aiohttp


SITES = constants.SITES


@constants.async_timer_decorator
async def download_all_sites(sites=SITES):
    async def download_site(url, session):
      async with session.get(url) as response:
          print(f"Read {len(await response.read())} bytes from {url}")

    async with aiohttp.ClientSession() as session:
        tasks = [download_site(url, session) for url in sites]
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
  asyncio.run(download_all_sites())
