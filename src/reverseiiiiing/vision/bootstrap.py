"""Auto-fetch TFT assets from CommunityDragon.

Downloads for the CURRENT live set:
  - Champion portraits  → data/templates/champs/<api_name>.png
  - Item icons          → data/templates/items/<api_name>.png
  - Trait icons         → data/templates/traits/<api_name>.png
  - Augment icons       → data/templates/augments/<api_name>.png
  - Full set JSON       → data/game_data.json  (reference by other modules)

Also writes a tiny data/manifest.json so main.exe can skip re-fetching
when assets are already present and current patch hasn't moved.

CommunityDragon updates per-patch. Users should re-run this (or just
restart main.exe with --refresh) when a new TFT patch drops.
"""
from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from pathlib import Path

import httpx

from reverseiiiiing.utils.logger import get_logger

log = get_logger(__name__)

CDRAGON_BASE = "https://raw.communitydragon.org/latest"
TFT_DATA_JSON = f"{CDRAGON_BASE}/cdragon/tft/en_us.json"


@dataclass
class SetInfo:
    number: int                 # e.g. 14
    name: str                   # e.g. "Cyber City"
    champions: list[dict]
    items: list[dict]
    traits: list[dict]
    augments: list[dict]


def _asset_url(path: str) -> str:
    """CommunityDragon serves game assets at a lowercased path under /game/."""
    if not path:
        return ""
    p = path.lower().replace("/lol-game-data/assets/", "")
    if p.endswith(".dds") or p.endswith(".tex"):
        p = re.sub(r"\.(dds|tex)$", ".png", p)
    return f"{CDRAGON_BASE}/game/{p}"


async def fetch_set_data(client: httpx.AsyncClient) -> SetInfo:
    r = await client.get(TFT_DATA_JSON, timeout=30)
    r.raise_for_status()
    data = r.json()

    # Pick the most recent set (highest "number" among sets with activeSet true)
    sets = data.get("sets", {})
    numbers = sorted(int(k) for k in sets.keys())
    latest = str(numbers[-1])
    s = sets[latest]

    log.info(f"Latest TFT set: {latest} — {s.get('name')}")
    return SetInfo(
        number=int(latest),
        name=s.get("name", ""),
        champions=s.get("champions", []),
        items=data.get("items", []),
        traits=s.get("traits", []),
        augments=[c for c in data.get("items", []) if "augment" in (c.get("from") or [])],
    )


async def _download_one(
    client: httpx.AsyncClient, url: str, dest: Path, semaphore: asyncio.Semaphore,
) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    async with semaphore:
        try:
            r = await client.get(url, timeout=20)
            if r.status_code != 200:
                return False
            dest.write_bytes(r.content)
            return True
        except Exception as e:
            log.debug(f"download failed {url}: {e}")
            return False


async def download_assets(info: SetInfo, out_dir: Path, concurrency: int = 16) -> dict:
    (out_dir / "champs").mkdir(parents=True, exist_ok=True)
    (out_dir / "items").mkdir(parents=True, exist_ok=True)
    (out_dir / "traits").mkdir(parents=True, exist_ok=True)
    (out_dir / "augments").mkdir(parents=True, exist_ok=True)

    sem = asyncio.Semaphore(concurrency)
    tasks: list[asyncio.Task] = []
    counts = {"champs": 0, "items": 0, "traits": 0, "augments": 0}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Champions — use the HUD "square" icon (small portrait, matches shop art)
        for c in info.champions:
            api_name = c.get("apiName") or c.get("name", "").replace(" ", "_")
            icon = c.get("squareIcon") or c.get("tileIcon") or ""
            url = _asset_url(icon)
            if not url:
                continue
            dest = out_dir / "champs" / f"{api_name}.png"
            tasks.append(asyncio.create_task(_download_one(client, url, dest, sem)))

        # Items (shared across sets)
        for it in info.items:
            api_name = it.get("apiName") or it.get("nameId", "")
            icon = it.get("icon") or it.get("squareIcon") or ""
            url = _asset_url(icon)
            if not api_name or not url:
                continue
            dest = out_dir / "items" / f"{api_name}.png"
            tasks.append(asyncio.create_task(_download_one(client, url, dest, sem)))

        # Traits
        for t in info.traits:
            api_name = t.get("apiName") or t.get("name", "").replace(" ", "_")
            icon = t.get("icon") or ""
            url = _asset_url(icon)
            if not url:
                continue
            dest = out_dir / "traits" / f"{api_name}.png"
            tasks.append(asyncio.create_task(_download_one(client, url, dest, sem)))

        results = await asyncio.gather(*tasks)

    # Tally
    for p in (out_dir / "champs").glob("*.png"):   counts["champs"] += 1
    for p in (out_dir / "items").glob("*.png"):    counts["items"] += 1
    for p in (out_dir / "traits").glob("*.png"):   counts["traits"] += 1
    for p in (out_dir / "augments").glob("*.png"): counts["augments"] += 1
    counts["downloaded_this_run"] = sum(1 for r in results if r)
    return counts


async def run(data_dir: str | Path = "data", refresh: bool = False) -> dict:
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = data_dir / "manifest.json"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        info = await fetch_set_data(client)

    manifest_existing = {}
    if manifest_path.exists():
        manifest_existing = json.loads(manifest_path.read_text())

    if (not refresh
            and manifest_existing.get("set_number") == info.number
            and manifest_existing.get("champions", 0) >= len(info.champions) * 0.9):
        log.info(f"Assets up-to-date for set {info.number}; skipping download. "
                 f"(use --refresh to force)")
        return manifest_existing

    log.info(f"Fetching assets for TFT set {info.number} — {info.name}")
    counts = await download_assets(info, data_dir / "templates")

    # Persist game data for lookups elsewhere
    (data_dir / "game_data.json").write_text(json.dumps({
        "set_number": info.number,
        "set_name": info.name,
        "champions": info.champions,
        "items": info.items,
        "traits": info.traits,
    }, ensure_ascii=False, indent=2))

    manifest = {
        "set_number": info.number,
        "set_name": info.name,
        "counts": counts,
        "champions": len(info.champions),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    log.info(f"Bootstrap done: {counts}")
    return manifest


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="reverseiii-bootstrap")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--refresh", action="store_true", help="Force re-download")
    args = ap.parse_args()
    asyncio.run(run(args.data_dir, args.refresh))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
