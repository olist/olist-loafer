import logging
from contextlib import asynccontextmanager

from aiobotocore.session import get_session

logger = logging.getLogger(__name__)

DEFAULT_SESSION = None


def _setup_default_session():
    global DEFAULT_SESSION  # noqa: PLW0603
    DEFAULT_SESSION = get_session()


def get_default_session():
    if not DEFAULT_SESSION:
        _setup_default_session()

    return DEFAULT_SESSION


class _BotoClient:
    boto_service_name = None

    def __init__(self, *, client=None, **client_options):
        if client:
            self._client = client
        else:
            self._client_options = {
                "api_version": client_options.get("api_version"),
                "aws_access_key_id": client_options.get("aws_access_key_id"),
                "aws_secret_access_key": client_options.get("aws_secret_access_key"),
                "aws_session_token": client_options.get("aws_session_token"),
                "endpoint_url": client_options.get("endpoint_url"),
                "region_name": client_options.get("region_name"),
                "use_ssl": client_options.get("use_ssl", True),
                "verify": client_options.get("verify"),
            }

    @asynccontextmanager
    async def get_client(self):
        if hasattr(self, "_client"):
            yield self._client
        else:
            async with get_default_session().create_client(self.boto_service_name, **self._client_options) as client:
                yield client


class BaseSQSClient(_BotoClient):
    boto_service_name = "sqs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_queue_urls = {}

    async def get_queue_url(self, queue):
        if queue and (queue.startswith(("http://", "https://"))):
            name = queue.split("/")[-1]
            self._cached_queue_urls[name] = queue
            queue = name

        if queue not in self._cached_queue_urls:
            async with self.get_client() as client:
                response = await client.get_queue_url(QueueName=queue)
                self._cached_queue_urls[queue] = response["QueueUrl"]

        return self._cached_queue_urls[queue]


class BaseSNSClient(_BotoClient):
    boto_service_name = "sns"

    async def get_topic_arn(self, topic):
        arn_prefix = "arn:aws:sns:"
        if topic.startswith(arn_prefix):
            return topic
        return f"{arn_prefix}*:{topic}"
