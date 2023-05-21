import logging

from .compat import iscoroutinefunction, to_thread

logger = logging.getLogger(__name__)


async def ensure_coroutinefunction(func, *args):
    if iscoroutinefunction(func):
        logger.debug(f"handler is coroutine! {func!r}")
        return await func(*args)

    logger.debug(f"handler will run in a separate thread: {func!r}")
    return await to_thread(func, *args)


def calculate_backoff_multiplier(number_of_tries, backoff_factor):
    exponential_factor = backoff_factor**number_of_tries

    return exponential_factor
