from types import EllipsisType
from typing import NotRequired, TypedDict

from types_aiobotocore_sqs import Client as SQSClient
from types_aiobotocore_sqs.type_defs import ReceiveMessageRequestQueueReceiveMessagesTypeDef

from loafer.message_translators import AbstractMessageTranslator
from loafer.routes import Route
from loafer.types import ErrorHandler, Handler, HandlerFunc

from .bases import ClientOptions
from .message_translators import SNSMessageTranslator, SQSMessageTranslator
from .providers import SQSProvider


class _ClientProviderOptions(TypedDict):
    options: NotRequired[ReceiveMessageRequestQueueReceiveMessagesTypeDef]
    client: NotRequired[SQSClient]


class _CustomProviderOptions(ClientOptions):
    options: NotRequired[ReceiveMessageRequestQueueReceiveMessagesTypeDef]


class SQSRoute(Route):
    def __init__(
        self,
        provider_queue: str,
        provider_options: _ClientProviderOptions | _CustomProviderOptions | None = None,
        *,
        handler: HandlerFunc | Handler,
        name: str = "",
        message_translator: AbstractMessageTranslator | None | EllipsisType = ...,
        error_handler: ErrorHandler | None = None,
    ):
        provider_options = provider_options or {}
        provider = SQSProvider(provider_queue, **provider_options)

        super().__init__(
            provider=provider,
            handler=handler,
            name=name or provider_queue,
            message_translator=message_translator if message_translator is not Ellipsis else SQSMessageTranslator(),
            error_handler=error_handler,
        )


class SNSQueueRoute(Route):
    def __init__(
        self,
        provider_queue: str,
        provider_options: _ClientProviderOptions | _CustomProviderOptions | None = None,
        *,
        handler: HandlerFunc | Handler,
        name: str = "",
        message_translator: AbstractMessageTranslator | None | EllipsisType = ...,
        error_handler: ErrorHandler | None = None,
    ):
        provider_options = provider_options or {}
        provider = SQSProvider(provider_queue, **provider_options)

        super().__init__(
            provider=provider,
            handler=handler,
            name=name or provider_queue,
            message_translator=message_translator if message_translator is not Ellipsis else SNSMessageTranslator(),
            error_handler=error_handler,
        )
