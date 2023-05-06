import asyncio
import logging
import sys

from .exceptions import DeleteMessage

logger = logging.getLogger(__name__)


class LoaferDispatcher:
    def __init__(self, routes, max_jobs=None):
        self.routes = routes
        jobs = max_jobs or len(routes) * 10
        self._semaphore = asyncio.Semaphore(jobs)

    async def dispatch_message(self, message, route):
        logger.debug(f"dispatching message to route={route}")
        confirm_message = False
        if not message:
            logger.warning(f"message will be ignored:\n{message!r}\n")
            return confirm_message

        async with self._semaphore:
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

    async def _process_message(self, message, route):
        confirmation = await self.dispatch_message(message, route)
        provider = route.provider
        if confirmation:
            await provider.confirm_message(message)
        else:
            await provider.message_not_processed(message)
        return confirmation

    async def _dispatch_provider(self, route, forever=True):
        while True:
            messages = await route.provider.fetch_messages()
            process_messages_tasks = [
                asyncio.create_task(self._process_message(message, route)) for message in messages
            ]

            await asyncio.gather(*process_messages_tasks)

            if not forever:
                break

    async def dispatch_providers(self, forever=True):
        dispatch_provider_tasks = [
            asyncio.create_task(self._dispatch_provider(route, forever)) for route in self.routes
        ]

        await asyncio.gather(*dispatch_provider_tasks)

    def stop(self):
        for route in self.routes:
            route.stop()
