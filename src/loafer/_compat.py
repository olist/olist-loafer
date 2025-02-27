import asyncio
import inspect
import logging
from collections.abc import Callable, Coroutine
from functools import partial
from typing import Any, ParamSpec, TypeVar

logger: logging.Logger = logging.getLogger(__name__)


_R = TypeVar("_R")
_P = ParamSpec("_P")


def ensure_coroutinefunction(func: Callable[_P, _R]) -> Callable[_P, Coroutine[Any, Any, _R]]:
    if inspect.iscoroutinefunction(func):
        logger.debug("handler is coroutine! %r", func)
        return func

    logger.debug("handler will run in a separate thread: %r", func)
    return partial(asyncio.to_thread, func)
