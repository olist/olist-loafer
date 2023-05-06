import asyncio
from unittest import mock

import pytest

from loafer.dispatchers import LoaferDispatcher
from loafer.exceptions import DeleteMessage
from loafer.routes import Route


@pytest.fixture
def provider():
    return mock.AsyncMock(
        fetch_messages=mock.AsyncMock(return_value=["message"]),
        confirm_message=mock.AsyncMock(),
        message_not_processed=mock.AsyncMock(),
    )


@pytest.fixture
def route(provider):
    message_translator = mock.Mock(translate=mock.Mock(return_value={"content": "message"}))
    route = mock.AsyncMock(
        provider=provider,
        handler=mock.Mock(),
        message_translator=message_translator,
        spec=Route,
    )
    return route


@pytest.mark.asyncio
async def test_dispatch_message(route):
    route.deliver = mock.AsyncMock(return_value="confirmation")
    dispatcher = LoaferDispatcher([route])

    message = "foobar"
    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation == "confirmation"

    assert route.deliver.called
    route.deliver.assert_called_once_with(message)


@pytest.mark.asyncio
@pytest.mark.parametrize("message", [None, ""])
async def test_dispatch_invalid_message(route, message):
    route.deliver = mock.AsyncMock()
    dispatcher = LoaferDispatcher([route])

    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation is False
    assert route.deliver.called is False


@pytest.mark.asyncio
async def test_dispatch_message_task_delete_message(route):
    route.deliver = mock.AsyncMock(side_effect=DeleteMessage)
    dispatcher = LoaferDispatcher([route])

    message = "rejected-message"
    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation is True

    assert route.deliver.called
    route.deliver.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_dispatch_message_task_error(route):
    exc = Exception()
    route.deliver = mock.AsyncMock(side_effect=exc)
    route.error_handler = mock.AsyncMock(return_value="confirmation")
    dispatcher = LoaferDispatcher([route])

    message = "message"
    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation == "confirmation"

    assert route.deliver.called is True
    route.deliver.assert_called_once_with(message)
    assert route.error_handler.called is True


@pytest.mark.asyncio
async def test_dispatch_message_task_cancel(route):
    route.deliver = mock.AsyncMock(side_effect=asyncio.CancelledError)
    dispatcher = LoaferDispatcher([route])

    message = "message"
    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation is False

    assert route.deliver.called
    route.deliver.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_message_processing(route):
    dispatcher = LoaferDispatcher([route])
    dispatcher.dispatch_message = mock.AsyncMock()
    await dispatcher._process_message("message", route)

    assert dispatcher.dispatch_message.called
    dispatcher.dispatch_message.assert_called_once_with("message", route)
    assert route.provider.confirm_message.called
    assert route.provider.message_not_processed.called is False
    route.provider.confirm_message.assert_called_once_with("message")


@pytest.mark.asyncio
async def test_message_processing_unsuccessfully(route):
    dispatcher = LoaferDispatcher([route])
    dispatcher.dispatch_message = mock.AsyncMock(return_value=False)
    await dispatcher._process_message("message", route)

    assert dispatcher.dispatch_message.called
    dispatcher.dispatch_message.assert_called_once_with("message", route)

    assert route.provider.message_not_processed.called
    assert route.provider.confirm_message.called is False
    route.provider.message_not_processed.assert_called_once_with("message")


@pytest.mark.asyncio
async def test_dispatch_provider(route):
    route.provider.fetch_messages = mock.AsyncMock(return_value=["message"])
    dispatcher = LoaferDispatcher([route])
    await dispatcher._dispatch_provider(route, forever=False)

    assert route.provider.fetch_messages.called
    assert route.provider.confirm_message.called
    assert route.provider.message_not_processed.called is False


@pytest.mark.asyncio
async def test_dispatch_without_tasks(route, event_loop):
    route.provider.fetch_messages = mock.AsyncMock(return_value=[])
    dispatcher = LoaferDispatcher([route])
    await dispatcher._dispatch_provider(route, forever=False)

    assert route.provider.fetch_messages.called
    assert route.provider.confirm_message.called is False
    assert route.provider.message_not_processed.called is False


@pytest.mark.asyncio
async def test_dispatch_providers(route, event_loop):
    dispatcher = LoaferDispatcher([route])
    dispatcher._dispatch_provider = mock.AsyncMock()
    await dispatcher.dispatch_providers(forever=False)

    dispatcher._dispatch_provider.assert_called_once_with(route, False)


@pytest.mark.asyncio
async def test_dispatch_providers_with_error(route, event_loop):
    route.provider.fetch_messages.side_effect = ValueError
    dispatcher = LoaferDispatcher([route])
    with pytest.raises(ValueError):
        await dispatcher.dispatch_providers(forever=False)


def test_dispatcher_stop(route):
    route.stop = mock.Mock()
    dispatcher = LoaferDispatcher([route])
    dispatcher.stop()
    assert route.stop.called
