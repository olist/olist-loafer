from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

from .dispatchers import LoaferDispatcher
from .runners import LoaferRunner

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .routes import Route

logger = logging.getLogger(__name__)


class LoaferManager:
    def __init__(
        self,
        routes: Sequence[Route],
        runner: LoaferRunner | None = None,
        queue_size: int | None = None,
        workers: int | None = None,
    ):
        if runner is None:
            self.runner = LoaferRunner(on_stop_callback=self.on_loop__stop)
        else:
            self.runner = runner

        self.dispatcher = LoaferDispatcher(routes, queue_size, workers)

    def run(self, forever=True, debug=False):  # noqa: FBT002
        loop = self.runner.loop
        self._future = asyncio.ensure_future(
            self.dispatcher.dispatch_providers(forever=forever),
            loop=loop,
        )

        self._future.add_done_callback(self.on_future__errors)
        if not forever:
            self._future.add_done_callback(self.runner.prepare_stop)

        start = "starting loafer, pid={}, forever={}"
        logger.info(start.format(os.getpid(), forever))
        self.runner.start(debug=debug)

    #
    # Callbacks
    #

    def on_future__errors(self, future):
        if future.cancelled():
            return self.runner.prepare_stop()

        exc = future.exception()
        # Unhandled errors crashes the event loop execution
        if isinstance(exc, BaseException):
            logger.critical("fatal error caught: %r", exc)
            self.runner.prepare_stop()
            return None
        return None

    def on_loop__stop(self):
        logger.info("cancel dispatcher operations ...")

        if hasattr(self, "_future"):
            self._future.cancel()

        self.dispatcher.stop()
