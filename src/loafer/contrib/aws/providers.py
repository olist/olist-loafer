import logging
from collections.abc import Iterable
from typing import Any, Unpack, overload

import botocore.exceptions
from types_aiobotocore_sqs import Client as SQSClient
from types_aiobotocore_sqs.type_defs import (
    ReceiveMessageRequestQueueReceiveMessagesTypeDef,
    ReceiveMessageResultTypeDef,
)

from loafer._compat import override
from loafer.exceptions import ProviderError
from loafer.providers import AbstractProvider
from loafer.types import Message

from .bases import BaseSQSClient, ClientOptions

logger = logging.getLogger(__name__)


class SQSProvider(AbstractProvider, BaseSQSClient):
    @overload
    def __init__(
        self,
        queue_name: str,
        options: ReceiveMessageRequestQueueReceiveMessagesTypeDef | None = None,
        *,
        client: SQSClient,
    ): ...

    @overload
    def __init__(
        self,
        queue_name: str,
        options: ReceiveMessageRequestQueueReceiveMessagesTypeDef | None = None,
        **client_options: Unpack[ClientOptions],
    ): ...

    def __init__(
        self, queue_name: str, options: ReceiveMessageRequestQueueReceiveMessagesTypeDef | None = None, **kwargs: Any
    ):
        self.queue_name: str = queue_name
        self._options: ReceiveMessageRequestQueueReceiveMessagesTypeDef = options or {}
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"<{type(self).__name__}: {self.queue_name}>"

    @override
    async def confirm_message(self, message: Message) -> None:
        receipt = message["ReceiptHandle"]
        logger.info("confirm message (ack/deletion), receipt=%r", receipt)

        queue_url = await self.get_queue_url(self.queue_name)
        async with self.get_client() as client:
            await client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt)

    async def fetch_messages(self) -> Iterable[Message]:
        logger.debug("fetching messages on %s", self.queue_name)
        queue_url: str = await self.get_queue_url(self.queue_name)
        async with self.get_client() as client:
            try:
                response: ReceiveMessageResultTypeDef = await client.receive_message(
                    QueueUrl=queue_url, **self._options
                )
            except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as exc:
                msg = f"error fetching messages from queue={self.queue_name}: {exc!s}"
                raise ProviderError(msg) from exc

        return response.get("Messages", [])

    def stop(self) -> None:
        logger.info("stopping %s", self)
        return super().stop()
