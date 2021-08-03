import logging
from typing import Any, Callable, Union

from aiokafka.errors import KafkaError

from .bases import KafkaService
from loafer.exceptions import ProviderError
from loafer.providers import AbstractStreamingProvider

logger = logging.getLogger(__name__)


class KafkaProvider(AbstractStreamingProvider, KafkaService):
    def __init__(
        self,
        topic_name: str,
        retry_topic: Union[None, str, Callable[[Any], str]] = None,
        options=None,
        **kwargs,
    ):
        self.topic_name = topic_name
        self._options = options or {}
        self.retry_topic = retry_topic if callable(retry_topic) else lambda m: retry_topic

        super().__init__(topic_name, kwargs)

    def __str__(self):
        return f"<{type(self).__name__}: {self.topic_name}>"

    async def fetch_messages(self):
        logger.debug(f"fetching messages on {self.topic_name}")
        async with self.get_consumer() as consumer:
            try:
                messages = await consumer.getmany(**self._options)
                await consumer.commit()
            except KafkaError as exc:
                raise ProviderError(f"error fetching messages from queue={self.topic_name}: {exc}") from exc

            return messages

    async def message_not_processed(self, message):
        header_map = {name: value for name, value in message.headers}
        receive_count = header_map.setdefault("ApproximateReceiveCount", 1) + 1
        header_map["ApproximateReceiveCount"] = receive_count
        topic_name = t if (t := self.retry_topic(message)) else message.topic

        async with self.get_producer() as producer:
            await producer.send_and_wait(
                topic_name,
                message.value,
                key=message.key,
                timestamp_ms=message.timestamp,
                headers=message.headers,
            )
