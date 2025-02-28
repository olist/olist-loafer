from typing import TYPE_CHECKING
from unittest import mock

import pytest

from loafer.types import AsyncErrorHandler

if TYPE_CHECKING:
    import sentry_sdk

    from loafer.ext.sentry import sentry_handler
    from loafer.types import ExcInfo
else:
    sentry_sdk = pytest.importorskip("sentry_sdk")

    from loafer.ext.sentry import sentry_handler

pytestmark = pytest.mark.asyncio


async def _run(handler: AsyncErrorHandler) -> bool:
    """Helper function to run the error_handler and run some checks."""
    exc = ValueError("test")
    exc_info: ExcInfo = (type(exc), exc, None)

    with mock.patch.object(sentry_sdk, "capture_exception") as mock_capture_exception:
        delete_message: bool = await handler(exc_info, "test")

    scope: sentry_sdk.Scope = sentry_sdk.get_current_scope()
    assert scope._extras["message"] == "test"  # noqa: SLF001
    mock_capture_exception.assert_called_once_with(exc_info)

    return delete_message


async def test_sentry_handler_default() -> None:
    """Test if sentry_handler captures exception and deletes message."""
    handler: AsyncErrorHandler = sentry_handler()

    delete_message: bool = await _run(handler)

    assert delete_message is False


@pytest.mark.parametrize("should_delete_message", [True, False])
async def test_sentry_handler_delete_message(should_delete_message: bool) -> None:  # noqa: FBT001
    """Test if sentry_handler captures exception and respects message deletion choice."""
    handler: AsyncErrorHandler = sentry_handler(delete_message=should_delete_message)

    delete_message: bool = await _run(handler)

    assert delete_message == should_delete_message


async def test_sentry_handler_with_custom_hub() -> None:
    """Test if passing a custom hub is deprecated."""
    with pytest.warns(DeprecationWarning, match="Hub"):
        handler: AsyncErrorHandler = sentry_handler(sentry_sdk)

    delete_message: bool = await _run(handler)

    assert delete_message is False


@pytest.mark.parametrize("should_delete_message", [True, False])
async def test_sentry_handler_with_positional_delete_message(should_delete_message: bool) -> None:  # noqa: FBT001
    """Test if passing delete_message as positional arugment is deprecated."""
    with (
        pytest.warns(DeprecationWarning, match="delete_message"),
        pytest.warns(DeprecationWarning, match="Hub"),
    ):
        handler: AsyncErrorHandler = sentry_handler(sentry_sdk, should_delete_message)

    delete_message: bool = await _run(handler)

    assert delete_message == should_delete_message


async def test_sentry_handler_with_positional_kw_delete_message() -> None:
    """Test if passing delete_message as positional arugment is deprecated."""
    with (
        pytest.warns(DeprecationWarning, match="Hub"),
        pytest.raises(ValueError, match="delete_message"),
    ):
        sentry_handler(sentry_sdk, True, delete_message=False)
