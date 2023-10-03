import asyncio
import logging
import sys

from .exceptions import DeleteMessage

logger = logging.getLogger(__name__)


class LoaferDispatcher:
    def __init__(self, routes):
        self.routes = routes

    async def dispatch_message(self, message, route):
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

    async def _process_message(self, message, route):
        confirmation = await self.dispatch_message(message, route)
        provider = route.provider
        if confirmation:
            await provider.confirm_message(message)
        else:
            await provider.message_not_processed(message)
        return confirmation

    async def dispatch_providers(self, forever=True):
        tasks = [asyncio.create_task(route.provider.fetch_messages()) for route in self.routes]
        while tasks:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            new_tasks = []
            process_messages_tasks = []
            for task, route in zip(tasks, self.routes):
                if task.done():
                    process_messages_tasks.extend(
                        [
                            asyncio.create_task(self._process_message(message, route))
                            for message in task.result()
                        ]
                    )

                    if forever:
                        new_tasks.append(asyncio.create_task(route.provider.fetch_messages()))
                else:
                    new_tasks.append(task)

            if process_messages_tasks:
                await asyncio.gather(*process_messages_tasks)

            tasks = new_tasks

    def stop(self):
        for route in self.routes:
            route.stop()
