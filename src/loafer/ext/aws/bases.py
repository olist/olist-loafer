from contextlib import AbstractAsyncContextManager, nullcontext
from typing import TYPE_CHECKING, Any, Generic, Literal, NotRequired, TypedDict, TypeVar, Unpack, cast, overload

from aiobotocore.session import AioSession, get_session
from types_aiobotocore_sns import Client as SNSClient
from types_aiobotocore_sqs import Client as SQSClient

if TYPE_CHECKING:
    from types_aiobotocore_sqs.type_defs import GetQueueUrlResultTypeDef

ClientT = TypeVar("ClientT", SNSClient, SQSClient)

DEFAULT_SESSION = None


def _setup_default_session() -> None:
    global DEFAULT_SESSION  # noqa: PLW0603
    DEFAULT_SESSION = get_session()


def get_default_session() -> AioSession:
    if not DEFAULT_SESSION:
        _setup_default_session()

    assert DEFAULT_SESSION  # noqa: S101
    return DEFAULT_SESSION


class ClientOptions(TypedDict):
    api_version: NotRequired[str | None]
    aws_access_key_id: NotRequired[str | None]
    aws_secret_access_key: NotRequired[str | None]
    aws_session_token: NotRequired[str | None]
    endpoint_url: NotRequired[str | None]
    region_name: NotRequired[str | None]
    use_ssl: NotRequired[bool]
    verify: NotRequired[str | bool | None]


class _BotoClient(Generic[ClientT]):
    boto_service_name: Literal["sns", "sqs"]

    @overload
    def __init__(self, *, client: ClientT): ...

    @overload
    def __init__(self, **client_options: Unpack[ClientOptions]): ...

    def __init__(self, *, client: ClientT | None = None, **client_options: Unpack[ClientOptions]):
        if client:
            self._client: ClientT = client
        else:
            self._client_options: ClientOptions = {
                "api_version": client_options.get("api_version"),
                "aws_access_key_id": client_options.get("aws_access_key_id"),
                "aws_secret_access_key": client_options.get("aws_secret_access_key"),
                "aws_session_token": client_options.get("aws_session_token"),
                "endpoint_url": client_options.get("endpoint_url"),
                "region_name": client_options.get("region_name"),
                "use_ssl": client_options.get("use_ssl", True),
                "verify": client_options.get("verify"),
            }

    def get_client(self) -> AbstractAsyncContextManager[ClientT, None]:
        if hasattr(self, "_client"):
            return nullcontext(self._client)

        return cast(
            AbstractAsyncContextManager[ClientT, None],
            get_default_session().create_client(self.boto_service_name, **self._client_options),
        )


class BaseSQSClient(_BotoClient[SQSClient]):
    boto_service_name: Literal["sqs"] = "sqs"

    @overload
    def __init__(self, *, client: SQSClient): ...

    @overload
    def __init__(self, **client_options: Unpack[ClientOptions]): ...

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._cached_queue_urls: dict[str, str] = {}

    async def get_queue_url(self, queue: str) -> str:
        if queue and (queue.startswith(("http://", "https://"))):
            name = queue.split("/")[-1]
            self._cached_queue_urls[name] = queue
            queue = name

        if queue not in self._cached_queue_urls:
            async with self.get_client() as client:
                response: GetQueueUrlResultTypeDef = await client.get_queue_url(QueueName=queue)
                self._cached_queue_urls[queue] = response["QueueUrl"]

        return self._cached_queue_urls[queue]


class BaseSNSClient(_BotoClient[SNSClient]):
    boto_service_name: Literal["sns"] = "sns"

    async def get_topic_arn(self, topic: str) -> str:
        arn_prefix = "arn:aws:sns:"
        if topic.startswith(arn_prefix):
            return topic
        return f"{arn_prefix}*:{topic}"
