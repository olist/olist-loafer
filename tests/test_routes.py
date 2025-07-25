from unittest import mock

import pytest

from loafer.message_translators import StringMessageTranslator
from loafer.routes import Route


def test_provider(dummy_provider):
    route = Route(dummy_provider, handler=mock.Mock())
    assert route.provider is dummy_provider


def test_provider_invalid():
    with pytest.raises(TypeError):
        Route("invalid-provider", handler=mock.Mock())


def test_name(dummy_provider):
    route = Route(dummy_provider, handler=mock.Mock(), name="foo")
    assert route.name == "foo"


def test_message_translator(dummy_provider):
    translator = StringMessageTranslator()
    route = Route(dummy_provider, handler=mock.Mock(), message_translator=translator)
    assert isinstance(route.message_translator, StringMessageTranslator)


def test_default_message_translator(dummy_provider):
    route = Route(dummy_provider, handler=mock.Mock())
    assert route.message_translator is None


def test_message_translator_invalid(dummy_provider):
    with pytest.raises(TypeError):
        Route(dummy_provider, handler=mock.Mock(), message_translator="invalid")


def test_apply_message_translator(dummy_provider):
    translator = StringMessageTranslator()
    translator.translate = mock.Mock(return_value={"content": "foobar", "metadata": {}})
    route = Route(dummy_provider, mock.Mock(), message_translator=translator)
    translated = route.apply_message_translator("message")
    assert translated["content"] == "foobar"
    assert translated["metadata"] == {}
    assert translator.translate.called
    translator.translate.assert_called_once_with("message")


def test_apply_message_translator_error(dummy_provider):
    translator = StringMessageTranslator()
    translator.translate = mock.Mock(return_value={"content": "", "metadata": {}})
    route = Route(dummy_provider, mock.Mock(), message_translator=translator)

    with pytest.raises(ValueError, match="failed to translate"):
        route.apply_message_translator("message")

    assert translator.translate.called
    translator.translate.assert_called_once_with("message")


@pytest.mark.asyncio
async def test_error_handler_unset(dummy_provider):
    route = Route(dummy_provider, mock.Mock())
    exc = TypeError()
    exc_info = (type(exc), exc, None)
    result = await route.error_handler(exc_info, "whatever")
    assert result is False


def test_error_handler_invalid(dummy_provider):
    with pytest.raises(TypeError):
        Route(dummy_provider, handler=mock.Mock(), error_handler="invalid")


@pytest.mark.asyncio
async def test_error_handler(dummy_provider):
    attrs = {}

    def error_handler(exc_info, message):
        attrs["exc_info"] = exc_info
        attrs["message"] = message
        return True

    # we cant mock regular functions in error handlers, because it will
    # be checked with inspect.iscoroutinefunction() and pass as coro
    route = Route(dummy_provider, mock.Mock(), error_handler=error_handler)
    exc = TypeError()
    exc_info = (type(exc), exc, "traceback")
    result = await route.error_handler(exc_info, "whatever")
    assert result is True
    assert attrs["exc_info"] == exc_info
    assert attrs["message"] == "whatever"


@pytest.mark.asyncio
async def test_error_handler_coroutine(dummy_provider):
    error_handler = mock.AsyncMock(return_value=True)
    route = Route(dummy_provider, mock.Mock(), error_handler=error_handler)
    exc = TypeError()
    exc_info = (type(exc), exc, "traceback")
    result = await route.error_handler(exc_info, "whatever")
    assert result is True
    assert error_handler.called
    error_handler.assert_called_once_with(exc_info, "whatever")


@pytest.mark.asyncio
async def test_handler_class_based(dummy_provider):
    class Handler:
        async def handle(self, *args, **kwargs):
            pass

    handler = Handler()
    route = Route(dummy_provider, handler=handler)
    assert route.handler == handler.handle


@pytest.mark.asyncio
async def test_handler_class_based_invalid(dummy_provider):
    class Handler:
        pass

    handler = Handler()
    with pytest.raises(TypeError, match="handler must be a callable object"):
        Route(dummy_provider, handler=handler)


@pytest.mark.asyncio
async def test_handler_invalid(dummy_provider):
    with pytest.raises(TypeError, match="handler must be a callable object"):
        Route(dummy_provider, "invalid-handler")


def test_route_stop(dummy_provider):
    dummy_provider.stop = mock.Mock()
    route = Route(dummy_provider, handler=mock.Mock())
    route.stop()

    assert dummy_provider.stop.called


def test_route_stop_with_handler_stop(dummy_provider):
    class Handler:
        def handle(self, *args):
            pass

    dummy_provider.stop = mock.Mock()
    handler = Handler()
    handler.stop = mock.Mock()
    route = Route(dummy_provider, handler)
    route.stop()

    assert dummy_provider.stop.called
    assert handler.stop.called


# FIXME: Improve all test_deliver* tests


@pytest.mark.asyncio
async def test_deliver(dummy_provider):
    attrs = {}

    def test_handler(*args, **kwargs):
        attrs["args"] = args
        attrs["kwargs"] = kwargs
        return True

    route = Route(dummy_provider, handler=test_handler)
    message = "test"
    result = await route.deliver(message)

    assert result is True
    assert message in attrs["args"]


@pytest.mark.asyncio
async def test_deliver_with_coroutine(dummy_provider):
    mock_handler = mock.AsyncMock(return_value=False)
    route = Route(dummy_provider, mock_handler)
    message = "test"
    result = await route.deliver(message)
    assert result is False
    assert mock_handler.called
    assert message in mock_handler.call_args[0]


@pytest.mark.asyncio
async def test_deliver_with_message_translator(dummy_provider):
    mock_handler = mock.AsyncMock(return_value=True)
    route = Route(dummy_provider, mock_handler)
    route.apply_message_translator = mock.Mock(return_value={"content": "whatever", "metadata": {}})
    result = await route.deliver("test")
    assert result is True
    assert route.apply_message_translator.called
    assert mock_handler.called
    mock_handler.assert_called_once_with("whatever", {})
