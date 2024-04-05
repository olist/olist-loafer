import asyncio
import logging
import sys
from contextlib import suppress
from typing import Any, Optional, Sequence

from .exceptions import DeleteMessage
from .routes import Route

logger = logging.getLogger(__name__)


class LoaferDispatcher:
    def __init__(
        self,
        routes: Sequence[Route],
        max_concurrency: Optional[int] = None,
    ) -> None:
        self.routes = routes
        self.max_concurrency = (
            max_concurrency if max_concurrency is not None else len(routes) * 10
        )

    async def dispatch_message(self, message: Any, route: Route) -> bool:
        logger.debug(f"dispatching message to route={route}")
        confirm_message = False
        if not message:
            logger.warning(f"message will be ignored:\n{message!r}\n")
            return confirm_message

        try:
            confirm_message = await route.deliver(message)
        except DeleteMessage:
            logger.info(f"explicit message deletion\n{message}\n")
            confirm_message = True
        except asyncio.CancelledError:
            msg = '"{!r}" was cancelled, the message will not be acknowledged:\n{}\n'
            logger.warning(msg.format(route.handler, message))
        except Exception as exc:
            logger.exception(f"{exc!r}")
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
        self, processing_queue: asyncio.Queue, forever: bool = True
    ) -> None:
        routes = [route for route in self.routes]
        tasks = [
            asyncio.create_task(route.provider.fetch_messages()) for route in routes
        ]

        while routes or tasks:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            new_routes = []
            new_tasks = []
            for task, route in zip(tasks, routes):
                if task.done():
                    for message in task.result():
                        await processing_queue.put((message, route))

                    if forever:
                        new_routes.append(route)
                        new_tasks.append(
                            asyncio.create_task(route.provider.fetch_messages())
                        )
                else:
                    new_routes.append(route)
                    new_tasks.append(task)

            routes = new_routes
            tasks = new_tasks

    async def _consume_messages(self, processing_queue: asyncio.Queue) -> None:
        with suppress(asyncio.CancelledError):
            while True:
                message, route = await processing_queue.get()
                asyncio.create_task(
                    self._process_message(message, route)
                ).add_done_callback(lambda _: processing_queue.task_done())

    async def dispatch_providers(self, forever: bool = True) -> None:
        processing_queue = asyncio.Queue(self.max_concurrency)
        provider_task = asyncio.create_task(
            self._fetch_messages(processing_queue, forever)
        )
        consumer_task = asyncio.create_task(self._consume_messages(processing_queue))

        async def join():
            await provider_task
            await processing_queue.join()
            consumer_task.cancel()

        joining_task = asyncio.create_task(join())

        await asyncio.gather(provider_task, consumer_task, joining_task)

    def stop(self) -> None:
        for route in self.routes:
            route.stop()
