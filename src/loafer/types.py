from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Any, Protocol, TypeAlias, TypedDict, runtime_checkable

ExcInfo: TypeAlias = tuple[type[BaseException], BaseException, TracebackType] | tuple[None, None, None]

Message = Any
Metadata = Any

SyncErrorHandler: TypeAlias = Callable[[ExcInfo, Message], bool]
AsyncErrorHandler: TypeAlias = Callable[[ExcInfo, Message], Awaitable[bool]]
ErrorHandler: TypeAlias = SyncErrorHandler | AsyncErrorHandler

SyncHandlerFunc: TypeAlias = Callable[[Message, Metadata], bool]
AsyncHandlerFunc: TypeAlias = Callable[[Message, Metadata], Awaitable[bool]]
HandlerFunc: TypeAlias = SyncHandlerFunc | AsyncHandlerFunc


@runtime_checkable
class SyncHandler(Protocol):
    def handle(self, message: Message, metadata: Metadata) -> bool: ...


@runtime_checkable
class AsyncHandler(Protocol):
    async def handle(self, message: Message, metadata: Metadata) -> bool: ...


Handler: TypeAlias = SyncHandler | AsyncHandler


class TranslatedMessage(TypedDict):
    content: Message
    metadata: Metadata
