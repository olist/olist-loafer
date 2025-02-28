from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Any, TypeAlias

ExcInfo: TypeAlias = tuple[type[BaseException], BaseException, TracebackType] | tuple[None, None, None]

Message = Any

SyncErrorHandler: TypeAlias = Callable[[ExcInfo, Message], bool]
AsyncErrorHandler: TypeAlias = Callable[[ExcInfo, Message], Awaitable[bool]]
ErrorHandler: TypeAlias = SyncErrorHandler | AsyncErrorHandler
