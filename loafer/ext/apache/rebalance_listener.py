import logging

from aiokafka.abc import ConsumerRebalanceListener

logger = logging.getLogger(__name__)


class KafkaRebalanceListener(ConsumerRebalanceListener):
    def __init__(self, consumer) -> None:
        self._consumer = consumer
        self._current_offsets = []

    def add_offset(self, topic, offset):
        logger.debug(f"add offset {topic} {offset}")
        self._current_offsets.append({topic: offset})
        logger.debug(f"current offsets updated {self._current_offsets}")

    def get_current_offsets(self):
        return self._current_offsets

    def clear_offsets(self):
        self._current_offsets.clear()

    async def on_partitions_revoked(self, revoked):
        logger.debug(f"following partitions revoked .... {revoked}")
        if self._current_offsets:
            await self._consumer.commit(tuple(self._current_offsets))
            logger.debug(f"following partitions commited .... {len(self._current_offsets)}")
            self.clear_offsets()
        return True

    def on_partitions_assigned(self, assigned):
        logger.debug(f"following partitions assigned .... {assigned}")
        return True
