import asyncio
import aiohttp

async def connect(session):
    async with session.get('https://shop.silpo.ua/category/m-iaso-kovbasni-vyroby-316') as resp:
        print(resp.status)


async def main():
    conn = aiohttp.TCPConnector(limit=5)
    timeout = aiohttp.ClientTimeout(total=1000)
    async with aiohttp.ClientSession() as session:
        jobs = [connect(session) for _ in range(50)]
        await asyncio.gather(*jobs)
        

asyncio.run(main())
