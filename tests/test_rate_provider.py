import asyncio
import json
import urllib.parse
import urllib.request

from currency_tracker.rate_provider import ExchangerateHostProvider


def test_fetch_rate_parses_response(monkeypatch):
    called_urls: list[str] = []

    class FakeResponse:
        def __init__(self, payload: dict) -> None:
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

        def read(self) -> bytes:  # pragma: no cover - json.load calls .read() internally
            return json.dumps(self.payload).encode()

    def fake_urlopen(request: urllib.request.Request, timeout: float):  # type: ignore[override]
        called_urls.append(request.full_url)
        return FakeResponse({"rates": {"KZT": 450.5}})

    async def run() -> float:
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        provider = ExchangerateHostProvider()
        return await provider.fetch_rate()

    rate = asyncio.run(run())

    expected_url = (
        "https://api.exchangerate.host/latest"
        f"?base={urllib.parse.quote('USD')}&symbols={urllib.parse.quote('KZT')}"
    )
    assert called_urls == [expected_url]
    assert rate == 450.5
