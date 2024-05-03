from contextlib import nullcontext as does_not_raise
from unittest import mock

import pytest
from botocore.exceptions import BotoCoreError, ClientError

from loafer.exceptions import ProviderError
from loafer.ext.aws.providers import SQSProvider


@pytest.mark.asyncio
async def test_confirm_message(mock_boto_session_sqs, boto_client_sqs):
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name")
        message = {"ReceiptHandle": "message-receipt-handle"}
        await provider.confirm_message(message)

        assert boto_client_sqs.delete_message.call_args == mock.call(
            QueueUrl=await provider.get_queue_url("queue-name"), ReceiptHandle="message-receipt-handle"
        )


@pytest.mark.asyncio
async def test_confirm_message_not_found(mock_boto_session_sqs, boto_client_sqs):
    error = ClientError(error_response={"ResponseMetadata": {"HTTPStatusCode": 404}}, operation_name="whatever")
    boto_client_sqs.delete_message.side_effect = error
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name")
        message = {"ReceiptHandle": "message-receipt-handle-not-found"}
        await provider.confirm_message(message)

        assert boto_client_sqs.delete_message.call_args == mock.call(
            QueueUrl=await provider.get_queue_url("queue-name"),
            ReceiptHandle="message-receipt-handle-not-found",
        )


@pytest.mark.asyncio
async def test_confirm_message_unknown_error(mock_boto_session_sqs, boto_client_sqs):
    error = ClientError(error_response={"ResponseMetadata": {"HTTPStatusCode": 400}}, operation_name="whatever")
    boto_client_sqs.delete_message.side_effect = error
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name")
        message = {"ReceiptHandle": "message-receipt-handle-not-found"}
        with pytest.raises(ClientError):
            await provider.confirm_message(message)


@pytest.mark.asyncio
async def test_fetch_messages(mock_boto_session_sqs, boto_client_sqs):
    options = {"WaitTimeSeconds": 5, "MaxNumberOfMessages": 10}
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name", options=options)
        messages = await provider.fetch_messages()

        assert len(messages) == 1
        assert messages[0]["Body"] == "test"

        assert boto_client_sqs.receive_message.call_args == mock.call(
            QueueUrl=await provider.get_queue_url("queue-name"),
            WaitTimeSeconds=options.get("WaitTimeSeconds"),
            MaxNumberOfMessages=options.get("MaxNumberOfMessages"),
        )


@pytest.mark.asyncio
async def test_fetch_messages_returns_empty(mock_boto_session_sqs, boto_client_sqs):
    options = {"WaitTimeSeconds": 5, "MaxNumberOfMessages": 10}
    boto_client_sqs.receive_message.return_value = {"Messages": []}
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name", options=options)
        messages = await provider.fetch_messages()

        assert messages == []

        assert boto_client_sqs.receive_message.call_args == mock.call(
            QueueUrl=await provider.get_queue_url("queue-name"),
            WaitTimeSeconds=options.get("WaitTimeSeconds"),
            MaxNumberOfMessages=options.get("MaxNumberOfMessages"),
        )


@pytest.mark.asyncio
async def test_fetch_messages_with_client_error(mock_boto_session_sqs, boto_client_sqs):
    with mock_boto_session_sqs:
        error = ClientError(error_response={"Error": {"Message": "unknown"}}, operation_name="whatever")
        boto_client_sqs.receive_message.side_effect = error

        provider = SQSProvider("queue-name")
        with pytest.raises(ProviderError):
            await provider.fetch_messages()


@pytest.mark.asyncio
async def test_fetch_messages_with_botocoreerror(mock_boto_session_sqs, boto_client_sqs):
    with mock_boto_session_sqs:
        error = BotoCoreError()
        boto_client_sqs.receive_message.side_effect = error

        provider = SQSProvider("queue-name")
        with pytest.raises(ProviderError):
            await provider.fetch_messages()


@pytest.mark.asyncio
async def test_custom_visibility_timeout(mock_boto_session_sqs, boto_client_sqs):
    options = {"WaitTimeSeconds": 5, "MaxNumberOfMessages": 10, "VisibilityTimeout": 60}
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name", options=options)
        messages = await provider.fetch_messages()

        assert len(messages) == 1
        assert messages[0]["Body"] == "test"

        assert boto_client_sqs.receive_message.call_args == mock.call(
            QueueUrl=await provider.get_queue_url("queue-name"),
            WaitTimeSeconds=options.get("WaitTimeSeconds"),
            MaxNumberOfMessages=options.get("MaxNumberOfMessages"),
            VisibilityTimeout=options.get("VisibilityTimeout"),
        )


@pytest.mark.asyncio
async def test_backoff_factor_options(mock_boto_session_sqs, boto_client_sqs):
    options = {"WaitTimeSeconds": 5, "MaxNumberOfMessages": 10, "BackoffFactor": 1.5}
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name", options=options)

        assert provider._backoff_factor == 1.5  # noqa: SLF001

        await provider.fetch_messages()

        _, receive_message_kwargs = boto_client_sqs.receive_message.call_args

        assert "BackoffFactor" not in receive_message_kwargs
        assert "AttributeNames" in receive_message_kwargs
        assert "ApproximateReceiveCount" in receive_message_kwargs["AttributeNames"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("options", "expected"),
    [
        ({}, ["ApproximateReceiveCount"]),
        ({"AttributeNames": []}, ["ApproximateReceiveCount"]),
        ({"AttributeNames": ["CreatedTimestamp"]}, ["ApproximateReceiveCount", "CreatedTimestamp"]),
        ({"AttributeNames": ["All"]}, ["All"]),
    ],
)
async def test_backoff_factor_options_with_attributes_names(mock_boto_session_sqs, boto_client_sqs, options, expected):
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name", options={"BackoffFactor": 1.5, **options})
        await provider.fetch_messages()

    _, receive_message_kwargs = boto_client_sqs.receive_message.call_args
    assert set(receive_message_kwargs["AttributeNames"]) == set(expected)
    assert len(receive_message_kwargs["AttributeNames"]) == len(expected)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("visibility", "backoff_multiplier", "expected"),
    [
        (30, 1.5, 45),
        (30, 1.75, 52),
        (60, 1.5, 90),
    ],
)
async def test_fetch_messages_using_backoff_factor(
    mock_boto_session_sqs, boto_client_sqs, visibility, backoff_multiplier, expected
):
    options = {
        "WaitTimeSeconds": 5,
        "MaxNumberOfMessages": 10,
        "AttributeNames": ["ApproximateReceiveCount"],
        "BackoffFactor": 1.5,
        "VisibilityTimeout": visibility,
    }
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name", options=options)
        message = {"ReceiptHandle": "message-receipt-handle", "Attributes": {"ApproximateReceiveCount": 2}}

        with mock.patch(
            "loafer.ext.aws.providers.calculate_backoff_multiplier", return_value=backoff_multiplier
        ) as mock_calculate_backoff:
            await provider.message_not_processed(message)

            mock_calculate_backoff.assert_called_once_with(2, 1.5)

        boto_client_sqs.change_message_visibility.assert_awaited_once_with(
            QueueUrl=await provider.get_queue_url("queue-name"),
            ReceiptHandle="message-receipt-handle",
            VisibilityTimeout=expected,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "expectation"),
    [
        (
            ClientError(error_response={"Error": {"Code": "InvalidParameterValue"}}, operation_name="whatever"),
            does_not_raise(),
        ),
        (
            ClientError(error_response={"Error": {"Code": "Other"}}, operation_name="whatever"),
            pytest.raises(ClientError),
        ),
    ],
    ids=["InvalidParameterValue", "AnyOtherError"],
)
async def test_fetch_messages_change_message_visibility_error(
    mock_boto_session_sqs, boto_client_sqs, error, expectation
):
    boto_client_sqs.change_message_visibility.side_effect = error
    options = {
        "WaitTimeSeconds": 5,
        "MaxNumberOfMessages": 10,
        "AttributeNames": ["ApproximateReceiveCount"],
        "BackoffFactor": 1.5,
        "VisibilityTimeout": 30,
    }
    with mock_boto_session_sqs:
        provider = SQSProvider("queue-name", options=options)
        message = {"ReceiptHandle": "message-receipt-handle", "Attributes": {"ApproximateReceiveCount": 2}}

        with expectation:
            await provider.message_not_processed(message)

        boto_client_sqs.change_message_visibility.assert_awaited_once_with(
            QueueUrl=await provider.get_queue_url("queue-name"),
            ReceiptHandle="message-receipt-handle",
            VisibilityTimeout=mock.ANY,
        )
