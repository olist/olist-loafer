import json
import logging
from collections.abc import Callable
from typing import Any, Unpack, overload

from types_aiobotocore_sns import Client as SNSClient
from types_aiobotocore_sns.type_defs import PublishResponseTypeDef
from types_aiobotocore_sqs import Client as SQSClient
from types_aiobotocore_sqs.type_defs import SendMessageResultTypeDef

from loafer.types import Message, Metadata

from .bases import BaseSNSClient, BaseSQSClient, ClientOptions

logger = logging.getLogger(__name__)


class SQSHandler(BaseSQSClient):
    queue_name: str | None = None

    @overload
    def __init__(self, queue_name: str | None = None, *, client: SQSClient): ...

    @overload
    def __init__(self, queue_name: str | None = None, **client_options: Unpack[ClientOptions]): ...

    def __init__(self, queue_name: str | None = None, **kwargs: Any):
        self.queue_name = queue_name or self.queue_name
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"<{type(self).__name__}: {self.queue_name}>"

    async def publish(
        self, message: Message, encoder: Callable[[Message], str] | None = json.dumps
    ) -> SendMessageResultTypeDef:
        if not self.queue_name:
            msg = f"{type(self).__name__}: missing queue_name attribute"
            raise ValueError(msg)

        if encoder:
            message = encoder(message)

        logger.debug("publishing, queue=%s, message=%s", self.queue_name, message)

        queue_url = await self.get_queue_url(self.queue_name)
        async with self.get_client() as client:
            return await client.send_message(QueueUrl=queue_url, MessageBody=message)

    async def handle(self, message: Message, metadata: Metadata) -> bool:  # noqa: ARG002
        return bool(await self.publish(message))


class SNSHandler(BaseSNSClient):
    topic: str | None = None

    @overload
    def __init__(self, topic: str | None = None, *, client: SNSClient): ...

    @overload
    def __init__(self, topic: str | None = None, **client_options: Unpack[ClientOptions]): ...

    def __init__(self, topic: str | None = None, **kwargs: Any):
        self.topic = topic or self.topic
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"<{type(self).__name__}: {self.topic}>"

    async def publish(
        self, message: Message, encoder: Callable[[Message], str] | None = json.dumps
    ) -> PublishResponseTypeDef:
        if not self.topic:
            msg = f"{type(self).__name__}: missing topic attribute"
            raise ValueError(msg)

        if encoder:
            message = encoder(message)

        topic_arn = await self.get_topic_arn(self.topic)
        logger.debug("publishing, topic=%s, message=%s", topic_arn, message)

        msg = json.dumps({"default": message})
        async with self.get_client() as client:
            return await client.publish(TopicArn=topic_arn, MessageStructure="json", Message=msg)

    async def handle(self, message: Message, metadata: Metadata) -> bool:  # noqa: ARG002
        return bool(await self.publish(message))
