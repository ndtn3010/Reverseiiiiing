"""Riot Live Client Data API poller.

The in-game HTTP server at 127.0.0.1:2999 exposes a few endpoints — but note:
Riot's local API does NOT send TFT shop, bench, board, items, or augments.
We only get: game time, active player name, gold (via scoreboard JSON? no —
TFT exposes very little). We mainly use this to detect:
  - game-is-running
  - current timer / phase hints
  - lobby size
Everything else (board, shop, HP for all players) must come from CV.
"""
from __future__ import annotations

import asyncio
import ssl
from dataclasses import dataclass
from typing import Any

import httpx

from reverseiiiiing.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class LiveSnapshot:
    running: bool
    game_time_s: float = 0.0
    raw: dict[str, Any] | None = None


class LiveClient:
    def __init__(self, base_url: str = "https://127.0.0.1:2999", verify_ssl: bool = False):
        self.base_url = base_url.rstrip("/")
        self.verify = ssl.create_default_context()
        if not verify_ssl:
            self.verify.check_hostname = False
            self.verify.verify_mode = ssl.CERT_NONE
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "LiveClient":
        self._client = httpx.AsyncClient(verify=self.verify, timeout=2.0)
        return self

    async def __aexit__(self, *_exc) -> None:
        if self._client:
            await self._client.aclose()

    async def snapshot(self) -> LiveSnapshot:
        assert self._client is not None
        try:
            r = await self._client.get(f"{self.base_url}/liveclientdata/allgamedata")
            r.raise_for_status()
            data = r.json()
            return LiveSnapshot(
                running=True,
                game_time_s=data.get("gameData", {}).get("gameTime", 0.0),
                raw=data,
            )
        except (httpx.HTTPError, httpx.ConnectError, ssl.SSLError):
            return LiveSnapshot(running=False)

    async def poll(self, interval_ms: int = 500):
        """Async generator yielding snapshots at a fixed rate."""
        while True:
            yield await self.snapshot()
            await asyncio.sleep(interval_ms / 1000)
