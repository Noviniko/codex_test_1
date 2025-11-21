from __future__ import annotations

import asyncio
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class RateProvider(Protocol):
    """Fetches an exchange rate."""

    async def fetch_rate(self) -> float:
        """Return the latest USD/KZT exchange rate."""


@dataclass
class ExchangerateHostProvider:
    """Rate provider using exchangerate.host API."""

    base_currency: str = "USD"
    quote_currency: str = "KZT"
    timeout: float = 10.0

    async def fetch_rate(self) -> float:
        return await asyncio.to_thread(self._fetch_rate_sync)

    def _fetch_rate_sync(self) -> float:
        url = (
            "https://api.exchangerate.host/latest"
            f"?base={urllib.parse.quote(self.base_currency)}&symbols={urllib.parse.quote(self.quote_currency)}"
        )
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request, timeout=self.timeout) as response:  # nosec: B310 - external API is intended
            payload = json.load(response)
        rates = payload.get("rates") or {}
        try:
            rate = float(rates[self.quote_currency])
        except (KeyError, TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ValueError("Unexpected response shape from exchangerate.host") from exc
        return rate


class FailingRateProvider(RateProvider):  # pragma: no cover - utility for examples
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error or RuntimeError("Rate provider failure")

    async def fetch_rate(self) -> float:
        await asyncio.sleep(0)
        raise self.error
