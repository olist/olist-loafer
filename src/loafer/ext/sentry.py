import warnings
from typing import overload

import sentry_sdk

from loafer._compat import deprecated
from loafer.types import ErrorHandler, ExcInfo, Message


@overload
def sentry_handler(*, delete_message: bool = False) -> ErrorHandler: ...


@overload
@deprecated("delete_message as a positional argument is deprecated.")
def sentry_handler(sdk_or_hub: sentry_sdk.Hub, delete_message: bool, /) -> ErrorHandler: ...  # noqa: FBT001


@overload
@deprecated("Passing a custom sentry_sdk or Hub is deprecated.")
def sentry_handler(sdk_or_hub: sentry_sdk.Hub, /) -> ErrorHandler: ...


@overload
@deprecated("Passing a custom sentry_sdk or Hub is deprecated.")
def sentry_handler(sdk_or_hub: sentry_sdk.Hub, *, delete_message: bool = False) -> ErrorHandler: ...


def sentry_handler(*args, delete_message=False) -> ErrorHandler:
    if len(args) == 2:  # noqa: PLR2004
        warnings.warn(
            "delete_message as a positional argument is deprecated.",
            category=DeprecationWarning,
            stacklevel=3,
        )
        *args, delete_message = args

    if len(args) == 1:
        warnings.warn(
            "Passing a custom sentry_sdk or Hub is deprecated.",
            category=DeprecationWarning,
            stacklevel=3,
        )

    def send_to_sentry(exc_info: ExcInfo, message: Message) -> bool:
        scope: sentry_sdk.Scope = sentry_sdk.get_current_scope()
        scope.set_extra("message", message)
        sentry_sdk.capture_exception(exc_info)
        return delete_message

    return send_to_sentry
