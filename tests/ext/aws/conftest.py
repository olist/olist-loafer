from unittest import mock

import pytest

# boto client methods mock


@pytest.fixture
def queue_url():
    queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/queue-name"
    return {"QueueUrl": queue_url}


@pytest.fixture
def sqs_message():
    message = {"Body": "test"}
    return {"Messages": [message]}


def sqs_send_message():
    return {
        "MessageId": "uuid",
        "MD5OfMessageBody": "md5",
        "ResponseMetada": {"RequestId": "uuid", "HTTPStatusCode": 200},
    }


@pytest.fixture
def sns_list_topics():
    return {"Topics": [{"TopicArn": "arn:aws:sns:region:id:topic-name"}]}


@pytest.fixture
def sns_publish():
    return {"ResponseMetadata": {"HTTPStatusCode": 200, "RequestId": "uuid"}, "MessageId": "uuid"}


# boto client mock


class ClientContextCreator:
    def __init__(self, client):
        self._client = client

    async def __aenter__(self):
        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def boto_client_sqs(queue_url, sqs_message):
    mock_client = mock.Mock()
    mock_client.get_queue_url = mock.AsyncMock(return_value=queue_url)
    mock_client.delete_message = mock.AsyncMock()
    mock_client.receive_message = mock.AsyncMock(return_value=sqs_message)
    mock_client.send_message = mock.AsyncMock(return_value=sqs_send_message)
    mock_client.change_message_visibility = mock.AsyncMock()
    mock_client.close = mock.AsyncMock()
    return mock_client


@pytest.fixture
def mock_boto_session_sqs(boto_client_sqs):
    mock_create_client = mock.Mock(return_value=ClientContextCreator(boto_client_sqs))
    return mock.patch(
        "loafer.ext.aws.bases.get_default_session", return_value=mock.Mock(create_client=mock_create_client)
    )


@pytest.fixture
def boto_client_sns(sns_publish):
    mock_client = mock.Mock()
    mock_client.publish = mock.AsyncMock(return_value=sns_publish)
    mock_client.close = mock.AsyncMock()
    return mock_client


@pytest.fixture
def mock_boto_session_sns(boto_client_sns):
    mock_create_client = mock.Mock(return_value=ClientContextCreator(boto_client_sns))
    return mock.patch(
        "loafer.ext.aws.bases.get_default_session", return_value=mock.Mock(create_client=mock_create_client)
    )
