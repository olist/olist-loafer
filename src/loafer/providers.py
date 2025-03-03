import abc
from collections.abc import Iterable

from .types import Message


class AbstractProvider(abc.ABC):
    @abc.abstractmethod
    async def fetch_messages(self) -> Iterable[Message]:
        """Return a sequence of messages to be processed.

        If no messages are available, this coroutine should return an empty list.
        """

    @abc.abstractmethod
    async def confirm_message(self, message: Message) -> None:
        """Confirm the message processing.

        After the message confirmation we should not receive the same message again.
        This usually means we need to delete the message in the provider.
        """

    async def message_not_processed(self, message: Message) -> None:
        """Perform actions when a message was not processed."""

    def stop(self) -> None:
        """Stop the provider.

        If needed, the provider should perform clean-up actions.
        This method is called whenever we need to shutdown the provider.
        """
