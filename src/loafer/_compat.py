import builtins
import sys

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

if sys.version_info >= (3, 11):
    from asyncio import TaskGroup, to_thread

    ExceptionGroup = builtins.ExceptionGroup
else:
    import asyncio
    import contextvars
    import functools

    from exceptiongroup import ExceptionGroup
    from taskgroup import TaskGroup

    async def to_thread(func, /, *args, **kwargs):
        loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()
        func_call = functools.partial(ctx.run, func, *args, **kwargs)
        return await loop.run_in_executor(None, func_call)


__all__ = [
    "ExceptionGroup",
    "ParamSpec",
    "TaskGroup",
    "to_thread",
]
