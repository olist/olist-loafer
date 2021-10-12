import asyncio
from unittest.mock import Mock

import pytest

try:
    from asynctest import CoroutineMock as AsyncMock
except ImportError:
    from unittest.mock import AsyncMock

from loafer.dispatchers import LoaferDispatcher
from loafer.exceptions import DeleteMessage
from loafer.routes import Route


@pytest.fixture
def provider():
    return AsyncMock(
        fetch_messages=AsyncMock(return_value=["message"]),
        confirm_message=AsyncMock(),
        message_not_processed=AsyncMock(),
    )


@pytest.fixture
def route(provider):
    message_translator = Mock(translate=Mock(return_value={"content": "message"}))
    route = AsyncMock(provider=provider, handler=Mock(), message_translator=message_translator, spec=Route)
    return route


@pytest.mark.asyncio
async def test_dispatch_message(route):
    route.deliver = AsyncMock(return_value="confirmation")
    dispatcher = LoaferDispatcher([route])

    message = "foobar"
    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation == "confirmation"

    assert route.deliver.called
    route.deliver.assert_called_once_with(message)


@pytest.mark.asyncio
@pytest.mark.parametrize("message", [None, ""])
async def test_dispatch_invalid_message(route, message):
    route.deliver = AsyncMock()
    dispatcher = LoaferDispatcher([route])

    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation is False
    assert route.deliver.called is False


@pytest.mark.asyncio
async def test_dispatch_message_task_delete_message(route):
    route.deliver = AsyncMock(side_effect=DeleteMessage)
    dispatcher = LoaferDispatcher([route])

    message = "rejected-message"
    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation is True

    assert route.deliver.called
    route.deliver.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_dispatch_message_task_error(route):
    exc = Exception()
    route.deliver = AsyncMock(side_effect=exc)
    route.error_handler = AsyncMock(return_value="confirmation")
    dispatcher = LoaferDispatcher([route])

    message = "message"
    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation == "confirmation"

    assert route.deliver.called is True
    route.deliver.assert_called_once_with(message)
    assert route.error_handler.called is True


@pytest.mark.asyncio
async def test_dispatch_message_task_cancel(route):
    route.deliver = AsyncMock(side_effect=asyncio.CancelledError)
    dispatcher = LoaferDispatcher([route])

    message = "message"
    confirmation = await dispatcher.dispatch_message(message, route)
    assert confirmation is False

    assert route.deliver.called
    route.deliver.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_message_processing(route):
    dispatcher = LoaferDispatcher([route])
    dispatcher.dispatch_message = AsyncMock()
    await dispatcher._process_message("message", route)

    assert dispatcher.dispatch_message.called
    dispatcher.dispatch_message.assert_called_once_with("message", route)
    assert route.provider.confirm_message.called
    assert route.provider.message_not_processed.called is False
    route.provider.confirm_message.assert_called_once_with("message")


@pytest.mark.asyncio
async def test_message_processing_unsuccessfully(route):
    dispatcher = LoaferDispatcher([route])
    dispatcher.dispatch_message = AsyncMock(return_value=False)
    await dispatcher._process_message("message", route)

    assert dispatcher.dispatch_message.called
    dispatcher.dispatch_message.assert_called_once_with("message", route)

    assert route.provider.message_not_processed.called
    assert route.provider.confirm_message.called is False
    route.provider.message_not_processed.assert_called_once_with("message")


@pytest.mark.asyncio
async def test_dispatch_tasks(route):
    route.provider.fetch_messages = AsyncMock(return_value=["message"])
    dispatcher = LoaferDispatcher([route])
    await dispatcher._dispatch_tasks()

    assert route.provider.fetch_messages.called
    assert route.provider.confirm_message.called
    assert route.provider.message_not_processed.called is False


@pytest.mark.asyncio
async def test_dispatch_without_tasks(route, event_loop):
    route.provider.fetch_messages = AsyncMock(return_value=[])
    dispatcher = LoaferDispatcher([route])
    await dispatcher._dispatch_tasks()

    assert route.provider.fetch_messages.called
    assert route.provider.confirm_message.called is False
    assert route.provider.message_not_processed.called is False


@pytest.mark.asyncio
async def test_dispatch_providers(route, event_loop):
    dispatcher = LoaferDispatcher([route])
    dispatcher._dispatch_tasks = AsyncMock()
    dispatcher.stop_providers = Mock()
    await dispatcher.dispatch_providers(forever=False)

    assert dispatcher._dispatch_tasks.called
    dispatcher._dispatch_tasks.assert_called_once_with()


@pytest.mark.asyncio
async def test_dispatch_providers_with_error(route, event_loop):
    route.provider.fetch_messages.side_effect = ValueError
    dispatcher = LoaferDispatcher([route])
    with pytest.raises(ValueError):
        await dispatcher.dispatch_providers(forever=False)


def test_dispatcher_stop(route):
    route.stop = Mock()
    dispatcher = LoaferDispatcher([route])
    dispatcher.stop()
    assert route.stop.called
