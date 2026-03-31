import asyncio
import httpx
from typing import Callable, Any, Coroutine
from .exceptions import JulesError, TransportError

async def async_retry(func: Callable[[], Coroutine[Any, Any, Any]], retries: int = 3, backoff: float = 0.2):
    for attempt in range(retries):
        try:
            return await func()
        except (httpx.RequestError, JulesError, TransportError):
            if attempt == retries - 1:
                raise
            await asyncio.sleep(backoff * (2 ** attempt))
