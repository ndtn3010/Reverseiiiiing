"""Our own MCP server. Exposes:
  - get_live_state()     — current GameState from running capture
  - get_current_patch()  — latest patch version + body
  - get_meta_comps(tier) — comps for current patch
  - recommend_move()     — run decision engine on current state

Reads from a shared in-process cache that the main loop writes to.
If main loop isn't running, tools return empty / stale state.
"""
from __future__ import annotations

import json
import threading
from typing import Any, Optional

from reverseiiiiing.meta.scraper import MetaDB
from reverseiiiiing.state.models import GameState


class StateCache:
    """Thread-safe single-slot cache. Main loop writes, MCP reads."""
    def __init__(self):
        self._lock = threading.Lock()
        self._state: Optional[GameState] = None

    def set(self, state: GameState) -> None:
        with self._lock:
            self._state = state

    def get(self) -> Optional[GameState]:
        with self._lock:
            return self._state.model_copy() if self._state else None


CACHE = StateCache()


def register_tools(server) -> None:
    """Wire tools onto an MCP server instance (duck-typed)."""

    @server.tool()
    async def get_live_state() -> dict:
        """Return the current cached game state from the running capture loop."""
        s = CACHE.get()
        if s is None:
            return {"ok": False, "error": "no game state cached (is the main loop running?)"}
        return {"ok": True, "state": s.model_dump()}

    @server.tool()
    async def get_current_patch() -> dict:
        db = MetaDB()
        v = db.latest_patch()
        return {"ok": v is not None, "patch": v}

    @server.tool()
    async def get_meta_comps(tier: str = "S") -> dict:
        db = MetaDB()
        v = db.latest_patch()
        if not v:
            return {"ok": False, "error": "no patch scraped yet"}
        return {"ok": True, "patch": v, "comps": db.comps_for_patch(v, tier)}

    @server.tool()
    async def recommend_move() -> dict:
        from reverseiiiiing.decision.engine import DecisionEngine, EngineConfig
        s = CACHE.get()
        if s is None:
            return {"ok": False, "error": "no state"}
        actions = DecisionEngine(EngineConfig()).plan(s)
        return {"ok": True, "actions": [a.model_dump() for a in actions]}
