import asyncio
import logging

from aiokafka import AIOKafkaConsumer

from loafer.exceptions import ProviderError, ProviderRuntimeError
from loafer.providers import AbstractProvider
from loafer.ext.apache.rebalance_listener import KafkaRebalanceListener


logger = logging.getLogger(__name__)


class KafkaSimpleProvider(AbstractProvider):
    def __init__(self, queue_name, options=None, **kwargs):
        self.queue_name = queue_name
        
        self._client_options = {
            'bootstrap_servers': kwargs.get("bootstrap_servers", None),
            'sasl_mechanism': kwargs.get("sasl_mechanism", None),
            'security_protocol': kwargs.get("security_protocol", "PLAINTEXT"),
            'sasl_plain_username': kwargs.get("sasl_plain_username", None),
            'sasl_plain_password': kwargs.get("sasl_plain_password", None),
            'ssl_context': kwargs.get("ssl_context", None),
            'group_id': kwargs.get("group_id", "mygroup"),
            'value_deserializer': kwargs.get("value_deserializer", None),
            'auto_offset_reset': kwargs.get("auto_offset_reset", "latest"),
            'enable_auto_commit': False, 
        }
        logger.debug(f"Start {self} with options: {self._client_options}")
        self._rebalance_listener = None


    def __str__(self):
        return f"<{type(self).__name__}: {self.queue_name}>"

    def get_client(self):
        consumer = AIOKafkaConsumer(**self._client_options)
        self._rebalance_listener = KafkaRebalanceListener(consumer)
        return consumer

    async def confirm_message(self, message):
        logger.info(f"confirm message (ack/deletion) key>{message.key} timestamp>{message.timestamp}")
        return True

    async def message_not_processed(self, message):
        logger.info(f"message_not_processed key>{message.key} timestamp>{message.timestamp}")
        raise Exception("Manda pra DLQ")

    async def fetch_messages(self):
        logger.debug(f"start fetching messages on {self.queue_name}")
        messages = []
        try:
            async with self.get_client() as client:

                client.subscribe([self.queue_name], listener=self._rebalance_listener)
                response = await client.getmany(max_records=10, timeout_ms=5 * 1000)

                for topic, topic_messages in response.items():
                    if topic_messages:
                        messages = messages + topic_messages
                        for msg in topic_messages:
                            logger.debug(f"message fetched key>{msg.key} timestamp>{msg.timestamp}")
                            self._rebalance_listener.add_offset(topic, msg.offset)

                await client.commit()
                logger.debug(f"fetching messages done {self.queue_name} {len(messages)} msgs")
                self._rebalance_listener.clear_offsets()
                
        except Exception as exc:
            raise ProviderError(f"error fetching messages from queue={self.queue_name}: {str(exc)}") from exc

        return messages or []

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
