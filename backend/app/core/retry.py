import asyncio
from typing import Callable


async def retry_async(func: Callable, retries: int = 3, delay: float = 1.0):
    last_exception = None

    for attempt in range(retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            await asyncio.sleep(delay * (attempt + 1))

    raise last_exception
