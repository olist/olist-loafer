import logging

import botocore.exceptions

from .bases import BaseSQSClient
from loafer.exceptions import ProviderError
from loafer.providers import AbstractProvider
from loafer.utils import calculate_backoff_multiplier

logger = logging.getLogger(__name__)


class SQSProvider(AbstractProvider, BaseSQSClient):
    def __init__(self, queue_name, options=None, **kwargs):
        self.queue_name = queue_name
        self._options = options or {}
        self._backoff_factor = self._options.pop("BackoffFactor", None)
        if self._backoff_factor is not None:
            attributes_names = self._options.get("AttributeNames", [])
            if "ApproximateReceiveCount" not in attributes_names and "All" not in attributes_names:
                attributes_names.append("ApproximateReceiveCount")
                self._options["AttributeNames"] = attributes_names

        super().__init__(**kwargs)

    def __str__(self):
        return f"<{type(self).__name__}: {self.queue_name}>"

    async def confirm_message(self, message):
        receipt = message["ReceiptHandle"]
        logger.info(f"confirm message (ack/deletion), receipt={receipt!r}")

        queue_url = await self.get_queue_url(self.queue_name)
        try:
            async with self.get_client() as client:
                return await client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt)
        except botocore.exceptions.ClientError as exc:
            if exc.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
                return True

            raise

    async def message_not_processed(self, message):
        receipt = message["ReceiptHandle"]
        if self._backoff_factor:
            backoff_multiplier = calculate_backoff_multiplier(
                int(message["Attributes"]["ApproximateReceiveCount"]),
                self._backoff_factor,
            )

            custom_visibility_timeout = round(backoff_multiplier * self._options.get("VisibilityTimeout", 30))
            logger.info(
                f"message not processed, receipt={receipt!r}, "
                f"custom_visibility_timeout={custom_visibility_timeout!r}"
            )
            queue_url = await self.get_queue_url(self.queue_name)
            async with self.get_client() as client:
                return await client.change_message_visibility(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt,
                    VisibilityTimeout=custom_visibility_timeout,
                )

    async def fetch_messages(self):
        logger.debug(f"fetching messages on {self.queue_name}")
        try:
            queue_url = await self.get_queue_url(self.queue_name)
            async with self.get_client() as client:
                response = await client.receive_message(QueueUrl=queue_url, **self._options)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as exc:
            raise ProviderError(f"error fetching messages from queue={self.queue_name}: {str(exc)}") from exc

        return response.get("Messages", [])

    def stop(self):
        logger.info(f"stopping {self}")
        return super().stop()
