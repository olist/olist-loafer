import asyncio
import logging

logger = logging.getLogger(__name__)


async def run_in_loop_or_executor(func, *args):
    if asyncio.iscoroutinefunction(func):
        logger.debug(f"handler is coroutine! {func!r}")
        return await func(*args)

    loop = asyncio.get_event_loop()
    logger.debug(f"handler will run in a separate thread: {func!r}")
    return await loop.run_in_executor(None, func, *args)


def calculate_backoff_multiplier(number_of_tries, backoff_factor):
    exponential_factor = backoff_factor**number_of_tries

    return exponential_factor
