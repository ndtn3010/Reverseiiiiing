"""Patch version detection and refresh orchestration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from . import cdragon
from .db import connect
from ..config import Config

log = logging.getLogger(__name__)


@dataclass
class PatchState:
    stored_version: str | None
    live_version: str | None
    stored_hash: str | None
    live_hash: str | None

    @property
    def version_changed(self) -> bool:
        return self.live_version != self.stored_version and self.live_version is not None

    @property
    def content_changed(self) -> bool:
        return self.live_hash != self.stored_hash and self.live_hash is not None


async def fetch_live_version(cfg: Config) -> str | None:
    """Try CDragon first (no auth), fall back to DDragon versions endpoint."""
    v = await cdragon.fetch_version(cfg)
    if v:
        return v
    try:
        async with httpx.AsyncClient(
            timeout=cfg.cdragon.timeout_sec,
            headers={"User-Agent": cfg.http.user_agent},
        ) as client:
            resp = await client.get(cfg.ddragon.versions_url)
            resp.raise_for_status()
            versions = resp.json()
            return versions[0] if versions else None
    except Exception as e:
        log.warning("ddragon version fetch failed: %s", e)
        return None


def current_stored_state(cfg: Config) -> tuple[str | None, str | None]:
    with connect(cfg.db.path) as conn:
        row = conn.execute(
            "SELECT version, cdragon_hash FROM patches ORDER BY detected_at DESC LIMIT 1"
        ).fetchone()
    if not row:
        return None, None
    return row["version"], row["cdragon_hash"]


async def diff_against_live(cfg: Config) -> PatchState:
    stored_version, stored_hash = current_stored_state(cfg)
    live_version = await fetch_live_version(cfg)
    live_hash: str | None = None
    try:
        raw = await cdragon.fetch(cfg)
        live_hash = raw.content_hash
    except Exception as e:
        log.warning("cdragon fetch for hash probe failed: %s", e)
    return PatchState(
        stored_version=stored_version,
        live_version=live_version,
        stored_hash=stored_hash,
        live_hash=live_hash,
    )


async def refresh_if_changed(cfg: Config, force: bool = False) -> dict:
    state = await diff_against_live(cfg)
    needs_refresh = force or state.version_changed or state.content_changed
    out: dict = {
        "stored_version": state.stored_version,
        "live_version": state.live_version,
        "stored_hash": state.stored_hash,
        "live_hash": state.live_hash,
        "refreshed": False,
    }
    if not needs_refresh:
        return out

    raw = await cdragon.fetch(cfg)
    version = state.live_version or "unknown"
    counts = cdragon.ingest(
        payload=raw.payload,
        set_id=cfg.set.current,
        patch_version=version,
        cdragon_hash=raw.content_hash,
        db_path=cfg.db.path,
    )
    out["refreshed"] = True
    out["counts"] = counts
    out["patch_written"] = version
    return out
