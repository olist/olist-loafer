import sys

PY311 = sys.version_info >= (3, 11)
PY312 = sys.version_info >= (3, 12)

if PY311:
    from asyncio import TaskGroup, to_thread
else:
    import asyncio
    import functools

    from taskgroup import TaskGroup

    async def to_thread(func, /, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


if PY312:
    from inspect import iscoroutinefunction
else:
    from asyncio import iscoroutinefunction


__all__ = [
    "to_thread",
    "iscoroutinefunction",
    "TaskGroup",
]
