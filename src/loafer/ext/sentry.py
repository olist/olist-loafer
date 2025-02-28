import warnings
from types import EllipsisType
from typing import overload

import sentry_sdk

from loafer._compat import deprecated
from loafer.types import ErrorHandler, ExcInfo, Message


@overload
def sentry_handler(*, delete_message: bool = False) -> ErrorHandler: ...


@overload
@deprecated("delete_message as a positional argument is deprecated.")
def sentry_handler(sdk_or_hub: sentry_sdk.Hub, should_delete: bool = False, /) -> ErrorHandler: ...  # noqa: FBT001, FBT002


def sentry_handler(
    sdk_or_hub: sentry_sdk.Hub | None = None,
    should_delete: bool | EllipsisType = ...,
    /,
    *,
    delete_message: bool | EllipsisType = ...,
) -> ErrorHandler:
    if sdk_or_hub:
        warnings.warn(
            "Passing a custom sentry_sdk or Hub is deprecated.",
            category=DeprecationWarning,
            stacklevel=3,
        )

    if delete_message is Ellipsis:
        delete_message = False
    elif should_delete is not Ellipsis:
        msg: str = "delete_message passed as both positional and keyword argument."
        raise ValueError(msg)

    if should_delete is not Ellipsis:
        warnings.warn(
            message="delete_message as a positional argument is deprecated.",
            category=DeprecationWarning,
            stacklevel=3,
        )
        delete_message = should_delete

    async def send_to_sentry(exc_info: ExcInfo, message: Message) -> bool:
        scope: sentry_sdk.Scope = sentry_sdk.get_current_scope()
        scope.set_extra("message", message)
        sentry_sdk.capture_exception(exc_info)
        return delete_message

    return send_to_sentry
