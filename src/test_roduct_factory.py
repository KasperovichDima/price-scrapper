from core.constants import TAVRIA_URL
from core.parsers.tavria import ProductFactory
import asyncio
import aiohttp


p = ProductFactory(
        url='/catalog/186/',
        category_name='Кондитерські вироби',
        subcategory_name='Печиво, вафлі',
        group_name='Печиво'
    )

async def test():
    connector = aiohttp.TCPConnector(limit=5)
    session = aiohttp.ClientSession(base_url=TAVRIA_URL, connector=connector)
    # async with mysession as session:
    await p.get_objects(session)

    await session.close()

asyncio.run(test())