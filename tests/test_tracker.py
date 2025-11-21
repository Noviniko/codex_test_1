import asyncio

from currency_tracker.tracker import ExchangeTracker


class StubRateProvider:
    def __init__(self, *rates: float) -> None:
        self._rates = asyncio.Queue()
        for rate in rates:
            self._rates.put_nowait(rate)

    async def fetch_rate(self) -> float:
        return await self._rates.get()


class RecordingNotifier:
    def __init__(self) -> None:
        self.events: list[tuple[float, float | None]] = []

    async def notify(self, rate: float, change: float | None) -> None:
        self.events.append((rate, change))


def test_poll_once_notifies_on_first_and_changes():
    async def run():
        provider = StubRateProvider(450.0, 451.0)
        notifier = RecordingNotifier()
        tracker = ExchangeTracker(provider=provider, notifier=notifier, change_tolerance=0.0)

        await tracker.poll_once()
        await tracker.poll_once()
        return notifier.events

    events = asyncio.run(run())
    assert events == [(450.0, None), (451.0, 1.0)]


def test_does_not_notify_when_change_below_tolerance():
    async def run():
        provider = StubRateProvider(450.0, 450.4)
        notifier = RecordingNotifier()
        tracker = ExchangeTracker(provider=provider, notifier=notifier, change_tolerance=0.5)

        await tracker.poll_once()
        await tracker.poll_once()
        return notifier.events

    events = asyncio.run(run())
    assert events == [(450.0, None)]
