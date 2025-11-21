from __future__ import annotations

import argparse
import asyncio
import logging
import signal
from contextlib import asynccontextmanager

from .notifier import ConsoleNotifier
from .rate_provider import ExchangerateHostProvider
from .tracker import ExchangeTracker

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track USD/KZT exchange rate changes")
    parser.add_argument("--interval", type=float, default=60.0, help="Polling interval in seconds (default: 60)")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.01,
        help="Minimum rate delta to trigger notifications (default: 0.01)",
    )
    parser.add_argument("--base", type=str, default="USD", help="Base currency (default: USD)")
    parser.add_argument("--quote", type=str, default="KZT", help="Quote currency (default: KZT)")
    return parser.parse_args()


@asynccontextmanager
def _tracker(args: argparse.Namespace):
    notifier = ConsoleNotifier()
    provider = ExchangerateHostProvider(base_currency=args.base, quote_currency=args.quote)
    tracker = ExchangeTracker(
        provider=provider,
        notifier=notifier,
        poll_interval=args.interval,
        change_tolerance=args.tolerance,
    )
    yield tracker
    tracker.stop()


def _setup_signal_handlers(tracker: ExchangeTracker) -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, tracker.stop)


async def main() -> None:
    args = parse_args()
    async with _tracker(args) as tracker:
        _setup_signal_handlers(tracker)
        logger.info(
            "Tracking %s/%s every %.1fs (tolerance=%.4f)",
            args.base,
            args.quote,
            args.interval,
            args.tolerance,
        )
        try:
            await tracker.run()
        except asyncio.CancelledError:  # pragma: no cover - for completeness
            pass


if __name__ == "__main__":
    asyncio.run(main())
