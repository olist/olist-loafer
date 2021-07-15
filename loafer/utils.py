import asyncio
import importlib
import logging
import os
import sys
from functools import wraps

logger = logging.getLogger(__name__)


def add_current_dir_to_syspath(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        current = os.getcwd()
        changed = False
        if current not in sys.path:
            sys.path.append(current)
            changed = True

        try:
            return f(*args, **kwargs)
        finally:
            # restore sys.path
            if changed is True:
                sys.path.remove(current)

    return wrapper


@add_current_dir_to_syspath
def import_callable(full_name):
    package, *name = full_name.rsplit(".", 1)
    try:
        module = importlib.import_module(package)
    except ValueError as exc:
        raise ImportError(f"Error trying to import {full_name!r}") from exc

    if name:
        handler = getattr(module, name[0])
    else:
        handler = module

    if not callable(handler):
        raise ImportError(f"{full_name!r} should be callable")

    return handler


async def run_in_loop_or_executor(func, *args):
    if asyncio.iscoroutinefunction(func):
        logger.debug(f"handler is coroutine! {func!r}")
        return await func(*args)

    loop = asyncio.get_event_loop()
    logger.debug(f"handler will run in a separate thread: {func!r}")
    return await loop.run_in_executor(None, func, *args)


def calculate_backoff_multiplier(number_of_tries, backoff_factor):
    exponential_factor = backoff_factor ** number_of_tries

    return exponential_factor
