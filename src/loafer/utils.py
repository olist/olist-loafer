import logging

from ._compat import iscoroutinefunction, to_thread

logger: logging.Logger = logging.getLogger(__name__)


async def ensure_coroutinefunction(func, *args):
    if iscoroutinefunction(func):
        logger.debug("handler is coroutine! %r", func)
        return await func(*args)

    logger.debug("handler will run in a separate thread: %r", func)
    return await to_thread(func, *args)
