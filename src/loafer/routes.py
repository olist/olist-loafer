import logging
from typing import Any

from ._compat import ensure_coroutinefunction
from .message_translators import AbstractMessageTranslator
from .providers import AbstractProvider
from .types import (
    AsyncErrorHandler,
    AsyncHandlerFunc,
    ErrorHandler,
    ExcInfo,
    Handler,
    HandlerFunc,
    Message,
    TranslatedMessage,
)

logger: logging.Logger = logging.getLogger(__name__)


class Route:
    def __init__(
        self,
        provider: AbstractProvider,
        handler: HandlerFunc | Handler,
        name: str = "default",
        message_translator: AbstractMessageTranslator | None = None,
        error_handler: ErrorHandler | None = None,
    ):
        self.name = name

        if not isinstance(provider, AbstractProvider):
            msg = f"invalid provider instance: {provider!r}"
            raise TypeError(msg)

        self.provider: AbstractProvider = provider

        if message_translator and not isinstance(message_translator, AbstractMessageTranslator):
            msg = f"invalid message translator instance: {message_translator!r}"
            raise TypeError(msg)

        self.message_translator: AbstractMessageTranslator | None = message_translator

        if error_handler and not callable(error_handler):
            msg = f"error_handler must be a callable object: {error_handler!r}"
            raise TypeError(msg)

        if error_handler:
            self._error_handler: AsyncErrorHandler | None = ensure_coroutinefunction(error_handler)
        else:
            self._error_handler = None

        self.handler: AsyncHandlerFunc
        self._handler_instance: Handler | None
        if callable(handler):
            self.handler = ensure_coroutinefunction(handler)
            self._handler_instance = None
        elif isinstance(handler, Handler):
            self.handler = ensure_coroutinefunction(handler.handle)
            self._handler_instance = handler
        else:
            msg = f"handler must be a callable object or implement `handle` method: {handler!r}"
            raise TypeError(msg)

    def __str__(self) -> str:
        return f"<{type(self).__name__}(name={self.name} provider={self.provider!r} handler={self.handler!r})>"

    def apply_message_translator(self, message: Any) -> TranslatedMessage:
        processed_message: TranslatedMessage = {"content": message, "metadata": {}}
        if not self.message_translator:
            return processed_message

        translated = self.message_translator.translate(processed_message["content"])
        processed_message["metadata"].update(translated.get("metadata", {}))
        processed_message["content"] = translated["content"]
        if not processed_message["content"]:
            msg = f"{self.message_translator} failed to translate message={message}"
            raise ValueError(msg)

        return processed_message

    async def deliver(self, raw_message: Message) -> bool:
        message: TranslatedMessage = self.apply_message_translator(raw_message)
        logger.info("delivering message route=%s, message=%r", self, message)
        return await self.handler(message["content"], message["metadata"])

    async def error_handler(self, exc_info: ExcInfo, message: Message) -> bool:
        logger.info("error handler process originated by message=%s", message)

        if self._error_handler is not None:
            return await self._error_handler(exc_info, message)

        return False

    def stop(self) -> None:
        logger.info("stopping route %s", self)
        self.provider.stop()
        # only for class-based handlers
        if self._handler_instance and hasattr(self._handler_instance, "stop"):
            self._handler_instance.stop()
