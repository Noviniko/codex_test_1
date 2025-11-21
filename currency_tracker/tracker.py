from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import AsyncIterator

from .notifier import Notifier
from .rate_provider import RateProvider

logger = logging.getLogger(__name__)


@dataclass
class ExchangeTracker:
    """Polls exchange rates and emits notifications when they change."""

    provider: RateProvider
    notifier: Notifier
    poll_interval: float = 60.0
    change_tolerance: float = 0.0
    _last_rate: float | None = field(default=None, init=False)
    _stop_event: asyncio.Event = field(default_factory=asyncio.Event, init=False)

    async def poll_once(self) -> float:
        """Fetch the latest rate and notify listeners if it changed."""
        try:
            rate = await self.provider.fetch_rate()
        except Exception:
            logger.exception("Failed to fetch exchange rate")
            raise

        if self._should_notify(rate):
            change = None if self._last_rate is None else rate - self._last_rate
            await self.notifier.notify(rate, change)
            self._last_rate = rate
        return rate

    def _should_notify(self, rate: float) -> bool:
        if self._last_rate is None:
            return True
        return abs(rate - self._last_rate) >= self.change_tolerance

    async def run(self) -> None:
        """Continuously poll until :meth:`stop` is called."""
        async for _ in self.poll_stream():
            pass

    async def poll_stream(self) -> AsyncIterator[float]:
        """Yield rates as they are polled, respecting stop signals."""
        while not self._stop_event.is_set():
            yield await self.poll_once()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.poll_interval)
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        """Signal the tracker to stop."""
        self._stop_event.set()
