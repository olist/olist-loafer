from __future__ import annotations

import asyncio
import logging
import sys
from typing import TYPE_CHECKING, Any

from ._compat import TaskGroup
from .exceptions import DeleteMessage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .routes import Route

logger = logging.getLogger(__name__)


class LoaferDispatcher:
    def __init__(
        self,
        routes: Sequence[Route],
        queue_size: int | None = None,
        workers: int | None = None,
    ) -> None:
        self.routes = routes
        self.queue_size = queue_size if queue_size is not None else len(routes) * 10
        self.workers = workers if workers is not None else max(len(routes), 5)

    async def dispatch_message(self, message: Any, route: Route) -> bool:
        logger.debug("dispatching message to route=%s", route)
        confirm_message = False
        if not message:
            logger.warning("message will be ignored:\n%r\n", message)
            return confirm_message

        try:
            confirm_message = await route.deliver(message)
        except DeleteMessage:
            logger.info("explicit message deletion\n%s\n", message)
            confirm_message = True
        except asyncio.CancelledError:
            msg = '"{!r}" was cancelled, the message will not be acknowledged:\n{}\n'
            logger.warning(msg.format(route.handler, message))
            raise
        except Exception as exc:
            logger.exception("%r", exc)  # noqa: TRY401
            exc_info = sys.exc_info()
            confirm_message = await route.error_handler(exc_info, message)

        return confirm_message

    async def _process_message(self, message: Any, route: Route) -> bool:
        confirmation = await self.dispatch_message(message, route)
        provider = route.provider
        if confirmation:
            await provider.confirm_message(message)
        else:
            await provider.message_not_processed(message)
        return confirmation

    async def _fetch_messages(
        self,
        processing_queue: asyncio.Queue,
        route: Route,
        forever: bool = True,  # noqa: FBT001, FBT002
    ) -> None:
        while True:
            messages = await route.provider.fetch_messages()
            for message in messages:
                await processing_queue.put((message, route))

            if not forever:
                break

    async def _consume_messages(self, processing_queue: asyncio.Queue, tg: TaskGroup) -> None:
        while True:
            message, route = await processing_queue.get()

            task = tg.create_task(self._process_message(message, route))
            await task
            processing_queue.task_done()

    async def dispatch_providers(self, forever: bool = True) -> None:  # noqa: FBT001, FBT002
        processing_queue = asyncio.Queue(self.queue_size)

        async with TaskGroup() as tg:
            provider_tasks = [
                tg.create_task(self._fetch_messages(processing_queue, route, forever)) for route in self.routes
            ]
            consumer_tasks = [tg.create_task(self._consume_messages(processing_queue, tg)) for _ in range(self.workers)]

            async def join():
                await asyncio.wait(provider_tasks)
                await processing_queue.join()

                for consumer_task in consumer_tasks:
                    consumer_task.cancel()

            tg.create_task(join())

    def stop(self) -> None:
        for route in self.routes:
            route.stop()
