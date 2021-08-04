import logging
from itertools import chain
from typing import Callable, Union

from aiokafka.errors import KafkaError

from .bases import KafkaService
from loafer.exceptions import ProviderError
from loafer.providers import AbstractStreamingProvider

logger = logging.getLogger(__name__)


class KafkaProvider(AbstractStreamingProvider, KafkaService):
    def __init__(
        self,
        topic_name: str,
        retry_topic: Union[None, str, Callable[[str, int], str]] = None,
        options=None,
        **kwargs,
    ):
        self.topic_name = topic_name
        self._options = options or {}
        self.retry_topic = retry_topic if callable(retry_topic) else lambda *_: retry_topic

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
                raise ProviderError(f"error fetching messages from topic={self.topic_name}: {exc!s}") from exc

            return chain.from_iterable(messages.values())

    async def message_not_processed(self, message):
        header_map = {name: value for name, value in message.headers}
        receive_count = header_map.setdefault("ApproximateReceiveCount", b"1").decode()
        receive_count = int(receive_count) + 1
        header_map["ApproximateReceiveCount"] = str(receive_count).encode()

        topic_name = self.retry_topic(message.topic, receive_count) or message.topic
        headers = list(header_map.items())

        logger.debug(f"publishing message to {topic_name}. receive_count={receive_count}")

        async with self.get_producer() as producer:
            try:
                await producer.send_and_wait(
                    topic_name,
                    message.value,
                    key=message.key,
                    timestamp_ms=message.timestamp,
                    headers=headers,
                )
            except (KafkaError, TypeError) as exc:
                logger.error(exc, exc_info=exc)
                raise ProviderError(f"error publishing messages to topic={topic_name}: {exc!s}") from exc
