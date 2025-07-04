import abc
import logging

from .types import Message, TranslatedMessage

logger = logging.getLogger(__name__)


class AbstractMessageTranslator(abc.ABC):
    @abc.abstractmethod
    def translate(self, message: Message) -> TranslatedMessage:
        """Translate a given message to an appropriate format to message processing.

        This method should return a `dict` instance with two keys: `content`
        and `metadata`.
        The `content` should contain the translated message and, `metadata` a
        dictionary with translation metadata or an empty `dict`.
        """


class StringMessageTranslator(AbstractMessageTranslator):
    def translate(self, message: Message) -> TranslatedMessage:
        logger.debug("%r will translate %r", type(self).__name__, message)
        return {"content": str(message), "metadata": {}}
