"""Tiny async retry helpers — keep call sites boring and bounded."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def retry_none(
    factory: Callable[[], Awaitable[T | None]],
    *,
    attempts: int = 2,
    delay: float = 0.4,
) -> T | None:
    """Call `factory` until it returns non-None, or `attempts` are exhausted."""
    if attempts < 1:
        return None
    last: T | None = None
    for i in range(attempts):
        last = await factory()
        if last is not None:
            return last
        if i + 1 < attempts and delay > 0:
            await asyncio.sleep(delay)
    return last
