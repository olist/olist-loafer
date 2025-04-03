import json
import logging

from loafer._compat import override
from loafer.message_translators import AbstractMessageTranslator
from loafer.types import Message, TranslatedMessage

logger = logging.getLogger(__name__)


class SQSMessageTranslator(AbstractMessageTranslator):
    @override
    def translate(self, message: Message) -> TranslatedMessage:
        translated: TranslatedMessage = {"content": None, "metadata": {}}
        try:
            body = message["Body"]
        except (KeyError, TypeError):
            logger.exception("missing Body key in SQS message. It really came from SQS ?\nmessage=%r", message)
            return translated

        try:
            translated["content"] = json.loads(body)
        except json.decoder.JSONDecodeError as exc:
            logger.exception("error=%r, message=%r", exc, message)  # noqa: TRY401
            return translated

        message.pop("Body")
        translated["metadata"].update(message)
        return translated


class SNSMessageTranslator(AbstractMessageTranslator):
    @override
    def translate(self, message: Message) -> TranslatedMessage:
        translated: TranslatedMessage = {"content": None, "metadata": {}}
        try:
            body = json.loads(message["Body"])
            message_body = body.pop("Message")
        except (KeyError, TypeError):
            logger.exception(
                "Missing Body or Message key in SQS message. It really came from SNS ?\nmessage=%r", message
            )
            return translated

        translated["metadata"].update(message)
        translated["metadata"].pop("Body")

        try:
            translated["content"] = json.loads(message_body)
        except (json.decoder.JSONDecodeError, TypeError) as exc:
            logger.exception("error=%r, message=%r", exc, message)  # noqa: TRY401
            return translated

        translated["metadata"].update(body)
        return translated
