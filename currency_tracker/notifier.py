from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class Notifier(Protocol):
    """Delivers notifications when a rate changes."""

    async def notify(self, rate: float, change: float | None) -> None:
        """Send a notification about the new rate and optional delta."""


class ConsoleNotifier:
    """Simple notifier that logs rate changes to stdout."""

    def __init__(self, *, logger_name: str | None = None) -> None:
        self.logger = logging.getLogger(logger_name or __name__)

    async def notify(self, rate: float, change: float | None) -> None:
        if change is None:
            message = f"USD/KZT rate observed: {rate:.4f}"
        else:
            direction = "increased" if change > 0 else "decreased"
            message = f"USD/KZT {direction} by {change:.4f} to {rate:.4f}"
        self.logger.info(message)


class LoggingNotifier(ConsoleNotifier):  # pragma: no cover - alias for compatibility
    """Backwards compatible alias for console notifier."""

    # Inherits all behaviour from ConsoleNotifier
