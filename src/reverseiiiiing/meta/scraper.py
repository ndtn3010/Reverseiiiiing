"""Patch + meta comps scraper → SQLite.

Sources:
  - Riot patch notes RSS → latest patch number + text
  - MetaTFT comps page → tier list, item builds
  - TFTAcademy → secondary source for validation

SQLite schema is simple: patches, comps, comp_units, comp_items.
Run nightly via Task Scheduler on Windows.
"""
from __future__ import annotations

import asyncio
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from reverseiiiiing.utils.logger import get_logger

log = get_logger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS patches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE,
    published_at TEXT,
    body_md TEXT,
    scraped_at TEXT
);
CREATE TABLE IF NOT EXISTS comps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patch_version TEXT,
    name TEXT,
    tier TEXT,
    carry TEXT,
    source TEXT,
    scraped_at TEXT,
    UNIQUE(patch_version, name, source)
);
CREATE TABLE IF NOT EXISTS comp_units (
    comp_id INTEGER,
    unit_api_name TEXT,
    star INTEGER,
    row_hint INTEGER,
    col_hint INTEGER,
    FOREIGN KEY(comp_id) REFERENCES comps(id)
);
CREATE TABLE IF NOT EXISTS comp_items (
    comp_id INTEGER,
    unit_api_name TEXT,
    item_api_name TEXT,
    priority INTEGER,
    FOREIGN KEY(comp_id) REFERENCES comps(id)
);
"""


@dataclass
class CompRow:
    name: str
    tier: str
    carry: str
    units: list[tuple[str, int]]   # (api_name, star)
    source: str


class MetaDB:
    def __init__(self, path: str | Path = "data/meta.sqlite"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    def latest_patch(self) -> str | None:
        row = self.conn.execute(
            "SELECT version FROM patches ORDER BY published_at DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else None

    def comps_for_patch(self, version: str, tier: str | None = None) -> list[dict]:
        q = "SELECT * FROM comps WHERE patch_version = ?"
        args: list = [version]
        if tier:
            q += " AND tier = ?"
            args.append(tier)
        cur = self.conn.execute(q, args)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def upsert_patch(self, version: str, published_at: str, body: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO patches(version, published_at, body_md, scraped_at)"
            " VALUES (?, ?, ?, ?)",
            (version, published_at, body, datetime.utcnow().isoformat()),
        )
        self.conn.commit()

    def upsert_comp(self, patch: str, comp: CompRow) -> int:
        cur = self.conn.execute(
            "INSERT OR REPLACE INTO comps(patch_version, name, tier, carry, source, scraped_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (patch, comp.name, comp.tier, comp.carry, comp.source,
             datetime.utcnow().isoformat()),
        )
        comp_id = cur.lastrowid
        self.conn.execute("DELETE FROM comp_units WHERE comp_id = ?", (comp_id,))
        for unit, star in comp.units:
            self.conn.execute(
                "INSERT INTO comp_units(comp_id, unit_api_name, star) VALUES (?, ?, ?)",
                (comp_id, unit, star),
            )
        self.conn.commit()
        return comp_id


# ─── Scrapers ────────────────────────────────────────────────────────────

async def scrape_patch_rss(client: httpx.AsyncClient, url: str) -> tuple[str, str, str] | None:
    """Return (version, published_at, body) for the latest patch."""
    try:
        r = await client.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "xml")
        item = soup.find("item")
        if not item:
            return None
        title = item.find("title").get_text(strip=True)
        pub = item.find("pubDate").get_text(strip=True) if item.find("pubDate") else ""
        body = item.find("description").get_text(strip=True) if item.find("description") else ""
        version = _extract_patch_version(title)
        return version, pub, body
    except Exception as e:
        log.warning(f"Patch RSS fetch failed: {e}")
        return None


def _extract_patch_version(title: str) -> str:
    import re
    m = re.search(r"\b(\d{1,2}\.\d{1,2}[a-z]?)\b", title.lower())
    return m.group(1) if m else "unknown"


async def scrape_metatft(client: httpx.AsyncClient, url: str) -> list[CompRow]:
    """VERY stubby placeholder — the real MetaTFT page uses React and
    exposes a JSON API behind the scenes. Need to reverse-engineer the
    actual endpoint for production. Returns empty for now."""
    log.info("metatft scraper: stub (returns 0 comps). Impl pending in v0.2.")
    return []


# ─── CLI ─────────────────────────────────────────────────────────────────

async def run_once(cfg: dict) -> None:
    db = MetaDB(cfg["meta"]["db_path"])
    async with httpx.AsyncClient(follow_redirects=True) as c:
        patch_data = await scrape_patch_rss(c, cfg["meta"]["scraper"]["patch_rss"])
        if patch_data:
            version, pub, body = patch_data
            db.upsert_patch(version, pub, body)
            log.info(f"Stored patch {version}")

            for src in cfg["meta"]["scraper"]["sources"]:
                if src["name"] == "metatft":
                    comps = await scrape_metatft(c, src["url"])
                    for comp in comps:
                        db.upsert_comp(version, comp)
                    log.info(f"Stored {len(comps)} comps from {src['name']}")
