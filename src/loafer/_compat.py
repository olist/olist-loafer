import asyncio
import inspect
import logging
import sys
from collections.abc import Awaitable, Callable
from functools import partial
from typing import ParamSpec, TypeVar, overload

logger: logging.Logger = logging.getLogger(__name__)


_R = TypeVar("_R")
_P = ParamSpec("_P")


@overload
def ensure_coroutinefunction(func: Callable[_P, _R]) -> Callable[_P, Awaitable[_R]]: ...


@overload
def ensure_coroutinefunction(func: Callable[_P, Awaitable[_R]]) -> Callable[_P, Awaitable[_R]]: ...


def ensure_coroutinefunction(func: Callable[_P, _R] | Callable[_P, Awaitable[_R]]) -> Callable[_P, Awaitable[_R]]:
    if inspect.iscoroutinefunction(func):
        logger.debug("handler is coroutine! %r", func)
        return func

    logger.debug("handler will run in a separate thread: %r", func)
    return partial(asyncio.to_thread, func)  # type: ignore[return-value]


if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

__all__ = [
    "deprecated",
    "ensure_coroutinefunction",
    "override",
]
