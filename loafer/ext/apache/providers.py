import asyncio
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import TopicPartition

from loafer.exceptions import ProviderError, ProviderRuntimeError
from loafer.providers import AbstractProvider
from loafer.utils import calculate_backoff_multiplier

logger = logging.getLogger(__name__)


class KafkaSimpleProvider(AbstractProvider):
    def __init__(self, queue_name, options=None, **kwargs):
        self.queue_name = queue_name

        self._client_options = {
            'bootstrap_servers': kwargs.get("bootstrap_servers", None),
            'group_id': kwargs.get("group_id", "mygroup"),
            'auto_offset_reset': kwargs.get("auto_offset_reset", "latest"),
            'enable_auto_commit': False, 
        }

    def __str__(self):
        return f"<{type(self).__name__}: {self.queue_name}>"

    def get_client(self):
        return AIOKafkaConsumer(self.queue_name, **self._client_options)

    async def confirm_message(self, message):
        logger.info(f"confirm message (ack/deletion)")
        print(f"confirm message (ack/deletion) topic > {message.topic} partition > {message.partition} offset> {message.offset}")
        try:
            async with self.get_client() as client:
                topic = TopicPartition(message.topic, message.partition)
                return await client.commit({topic: message.offset + 1})
        except Exception as exc:
            raise

    async def message_not_processed(self, message):
        raise Exception("Manda pra DLQ")

    async def fetch_messages(self):
        logger.debug(f"fetching messages on {self.queue_name}")
        try:
            async with self.get_client() as client:
                #await client.start()
                response = await client.getone()
        except Exception as exc:
            raise ProviderError(f"error fetching messages from queue={self.queue_name}: {str(exc)}") from exc

        return [response] or []

    async def _client_stop(self):
        async with self.get_client() as client:
            await client.stop()

    def stop(self):
        logger.info(f"stopping {self}")
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._client_stop())
        except RuntimeError as exc:
            raise ProviderRuntimeError() from exc
        return True
