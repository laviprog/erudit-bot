import asyncio

from src.api import start_api
from src.bot import start_bot


async def main():
    bot_task = asyncio.create_task(start_bot())
    api_task = asyncio.create_task(start_api())
    await asyncio.gather(bot_task, api_task)

if __name__ == "__main__":
    asyncio.run(main())
