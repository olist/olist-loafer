import logging

from ._compat import ensure_coroutinefunction
from .message_translators import AbstractMessageTranslator
from .providers import AbstractProvider

logger = logging.getLogger(__name__)


class Route:
    def __init__(self, provider, handler, name="default", message_translator=None, error_handler=None):
        self.name = name

        if not isinstance(provider, AbstractProvider):
            msg = f"invalid provider instance: {provider!r}"
            raise TypeError(msg)

        self.provider = provider

        if message_translator and not isinstance(message_translator, AbstractMessageTranslator):
            msg = f"invalid message translator instance: {message_translator!r}"
            raise TypeError(msg)

        self.message_translator = message_translator

        if error_handler and not callable(error_handler):
            msg = f"error_handler must be a callable object: {error_handler!r}"
            raise TypeError(msg)

        if error_handler:
            self._error_handler = ensure_coroutinefunction(error_handler)
        else:
            self._error_handler = None

        if callable(handler):
            self.handler = ensure_coroutinefunction(handler)
            self._handler_instance = None
        elif hasattr(handler, "handle"):
            self.handler = ensure_coroutinefunction(handler.handle)
            self._handler_instance = handler
        else:
            msg = f"handler must be a callable object or implement `handle` method: {handler!r}"
            raise ValueError(msg)

    def __str__(self):
        return f"<{type(self).__name__}(name={self.name} provider={self.provider!r} handler={self.handler!r})>"

    def apply_message_translator(self, message):
        processed_message = {"content": message, "metadata": {}}
        if not self.message_translator:
            return processed_message

        translated = self.message_translator.translate(processed_message["content"])
        processed_message["metadata"].update(translated.get("metadata", {}))
        processed_message["content"] = translated["content"]
        if not processed_message["content"]:
            msg = f"{self.message_translator} failed to translate message={message}"
            raise ValueError(msg)

        return processed_message

    async def deliver(self, raw_message):
        message = self.apply_message_translator(raw_message)
        logger.info("delivering message route=%s, message=%r", self, message)
        return await self.handler(message["content"], message["metadata"])

    async def error_handler(self, exc_info, message):
        logger.info("error handler process originated by message=%s", message)

        if self._error_handler is not None:
            return await self._error_handler(exc_info, message)

        return False

    def stop(self):
        logger.info("stopping route %s", self)
        self.provider.stop()
        # only for class-based handlers
        if hasattr(self._handler_instance, "stop"):
            self._handler_instance.stop()
