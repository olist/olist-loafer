import asyncio
import logging
import sys
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any, TypeAlias

from .exceptions import DeleteMessage
from .routes import Route
from .types import ExcInfo, Message

if TYPE_CHECKING:
    from loafer.providers import AbstractProvider

logger: logging.Logger = logging.getLogger(__name__)

ProcessingQueue: TypeAlias = asyncio.Queue[tuple[Route, Message]]


class LoaferDispatcher:
    def __init__(
        self,
        routes: Sequence[Route],
        queue_size: int | None = None,
        workers: int | None = None,
    ) -> None:
        self.routes: Sequence[Route] = routes
        self.queue_size: int = queue_size if queue_size is not None else len(routes) * 10
        self.workers: int = workers if workers is not None else max(len(routes), 5)

    async def dispatch_message(self, message: Message, route: Route) -> bool:
        logger.debug("dispatching message to route=%s", route)
        confirm_message: bool = False
        if not message:
            logger.warning("message will be ignored:\n%r\n", message)
            return confirm_message

        try:
            confirm_message = await route.deliver(message)
        except DeleteMessage:
            logger.info("explicit message deletion\n%s\n", message)
            confirm_message = True
        except asyncio.CancelledError:
            msg: str = '"{!r}" was cancelled, the message will not be acknowledged:\n{}\n'
            logger.warning(msg.format(route.handler, message))
            raise
        except Exception as exc:
            logger.exception("%r", exc)  # noqa: TRY401
            exc_info: ExcInfo = sys.exc_info()
            confirm_message = await route.error_handler(exc_info, message)

        return confirm_message

    async def _process_message(self, message: Any, route: Route) -> bool:
        confirmation: bool = await self.dispatch_message(message, route)
        provider: AbstractProvider = route.provider
        if confirmation:
            await provider.confirm_message(message)
        else:
            await provider.message_not_processed(message)
        return confirmation

    async def _fetch_messages(
        self,
        processing_queue: ProcessingQueue,
        route: Route,
        *,
        forever: bool = True,
    ) -> None:
        while True:
            messages: Iterable[Any] = await route.provider.fetch_messages()
            for message in messages:
                await processing_queue.put((message, route))

            if not forever:
                break

    async def _consume_messages(self, processing_queue: ProcessingQueue, tg: asyncio.TaskGroup) -> None:
        while True:
            message, route = await processing_queue.get()

            task = tg.create_task(self._process_message(message, route))
            await task
            processing_queue.task_done()

    async def dispatch_providers(self, *, forever: bool = True) -> None:
        processing_queue: ProcessingQueue = ProcessingQueue(self.queue_size)

        async with asyncio.TaskGroup() as tg:
            provider_tasks: list[asyncio.Task[None]] = [
                tg.create_task(self._fetch_messages(processing_queue, route, forever=forever)) for route in self.routes
            ]
            consumer_tasks: list[asyncio.Task[None]] = [
                tg.create_task(self._consume_messages(processing_queue, tg)) for _ in range(self.workers)
            ]

            async def join() -> None:
                await asyncio.wait(provider_tasks)
                await processing_queue.join()

                for consumer_task in consumer_tasks:
                    consumer_task.cancel()

            tg.create_task(join())

    def stop(self) -> None:
        for route in self.routes:
            route.stop()
