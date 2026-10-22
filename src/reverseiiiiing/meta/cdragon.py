"""CommunityDragon TFT data puller.

CDragon publishes the compiled TFT static data as a single JSON blob at
`<base>/cdragon/tft/<locale>.json`. No auth, no rate limit.

Known top-level shape (as of Set 18, from community mirrors):

    {
        "setData": [
            {
                "mutator": "TFTSet18",
                "number": 18,
                "name": "Enchanted Wilds",
                "champions": [{apiName, name, cost, stats, ability, traits}, ...],
                "traits":    [{apiName, name, effects, ...}, ...]
            },
            ...
        ],
        "items": [{apiName, name, composition, effects, incompatibleTraits, ...}, ...]
    }

Schema drifts between patches. This puller logs any unknown keys and continues.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from .db import connect, transaction, upsert_champion, upsert_item, upsert_patch, upsert_trait
from ..config import Config

log = logging.getLogger(__name__)


@dataclass
class CDragonRaw:
    payload: dict[str, Any]
    content_hash: str


async def fetch(cfg: Config) -> CDragonRaw:
    url = cfg.cdragon.base_url + cfg.cdragon.tft_json_path
    async with httpx.AsyncClient(
        timeout=cfg.cdragon.timeout_sec,
        headers={"User-Agent": cfg.http.user_agent},
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        body = resp.content
        payload = resp.json()
    content_hash = hashlib.sha256(body).hexdigest()[:16]
    return CDragonRaw(payload=payload, content_hash=content_hash)


async def fetch_version(cfg: Config) -> str | None:
    url = cfg.cdragon.base_url + cfg.cdragon.content_metadata
    async with httpx.AsyncClient(
        timeout=cfg.cdragon.timeout_sec,
        headers={"User-Agent": cfg.http.user_agent},
    ) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return None
        return resp.json().get("version")


def _find_set(payload: dict, set_id: int) -> dict | None:
    set_data = payload.get("setData") or []
    for entry in set_data:
        if entry.get("number") == set_id:
            return entry
    sets_dict = payload.get("sets") or {}
    return sets_dict.get(str(set_id))


def _parse_champion(raw: dict, set_id: int, patch: str | None) -> dict:
    stats = raw.get("stats") or {}
    ability = raw.get("ability") or {}
    traits = raw.get("traits") or []

    def _as_int(v: Any) -> int | None:
        if v is None:
            return None
        try:
            return int(round(float(v)))
        except (TypeError, ValueError):
            return None

    def _as_float(v: Any) -> float | None:
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    return {
        "champ_id": raw.get("apiName") or raw.get("name"),
        "set_id": set_id,
        "name": raw.get("name") or raw.get("apiName"),
        "cost": _as_int(raw.get("cost")) or 1,
        "hp_1star": _as_int(stats.get("hp")),
        "ad_1star": _as_int(stats.get("damage") or stats.get("attackDamage")),
        "armor": _as_int(stats.get("armor")),
        "mr": _as_int(stats.get("magicResist") or stats.get("mr")),
        "as_base": _as_float(stats.get("attackSpeed") or stats.get("as")),
        "range": _as_int(stats.get("range")),
        "mana_start": _as_int(stats.get("initialMana") or stats.get("startMana")),
        "mana_max": _as_int(stats.get("mana") or stats.get("maxMana")),
        "ability": {
            "name": ability.get("name"),
            "desc": ability.get("desc"),
            "variables": ability.get("variables"),
        },
        "traits": traits,
        "patch_version": patch,
    }


def _parse_trait(raw: dict, set_id: int, patch: str | None) -> dict:
    effects = raw.get("effects") or []
    breakpoints = [e.get("minUnits") for e in effects if e.get("minUnits") is not None]
    effects_by_bp = {
        str(e.get("minUnits")): {
            "max_units": e.get("maxUnits"),
            "variables": e.get("variables") or {},
            "style": e.get("style"),
        }
        for e in effects
    }
    return {
        "trait_id": raw.get("apiName") or raw.get("name"),
        "set_id": set_id,
        "name": raw.get("name") or raw.get("apiName"),
        "breakpoints": breakpoints,
        "effects": effects_by_bp,
        "champions": raw.get("champions") or [],
        "patch_version": patch,
    }


def _parse_item(raw: dict, patch: str | None) -> dict:
    composition = raw.get("composition") or raw.get("from") or []
    api = raw.get("apiName") or raw.get("name") or ""
    is_radiant = "radiant" in api.lower() or raw.get("isRadiant") is True
    is_ornn = raw.get("isUnique", False) and "ornn" in api.lower()
    is_emblem = "emblem" in api.lower() or "spatulaitem" in api.lower()

    return {
        "item_id": api,
        "name": raw.get("name") or api,
        "recipe": "+".join(composition) if composition else None,
        "stats": raw.get("effects") or raw.get("stats") or {},
        "effect_description": raw.get("desc"),
        "is_radiant": is_radiant,
        "is_ornn": is_ornn,
        "is_emblem": is_emblem,
        "unique_flag": bool(raw.get("unique", True)),
        "patch_version": patch,
    }


def ingest(payload: dict, set_id: int, patch_version: str, cdragon_hash: str,
           db_path: str) -> dict[str, int]:
    """Write parsed CDragon payload into the SQLite DB. Returns counts per table."""
    set_entry = _find_set(payload, set_id)
    if not set_entry:
        raise ValueError(f"Set {set_id} not found in CDragon payload")

    champs_raw = set_entry.get("champions") or []
    traits_raw = set_entry.get("traits") or []
    items_raw = payload.get("items") or []

    counts = {"champions": 0, "traits": 0, "items": 0}

    with connect(db_path) as conn, transaction(conn):
        upsert_patch(conn, patch_version, cdragon_hash=cdragon_hash)

        for champ in champs_raw:
            try:
                upsert_champion(conn, _parse_champion(champ, set_id, patch_version))
                counts["champions"] += 1
            except Exception as e:
                log.warning("champion skip %s: %s", champ.get("apiName"), e)

        for trait in traits_raw:
            try:
                upsert_trait(conn, _parse_trait(trait, set_id, patch_version))
                counts["traits"] += 1
            except Exception as e:
                log.warning("trait skip %s: %s", trait.get("apiName"), e)

        for item in items_raw:
            try:
                upsert_item(conn, _parse_item(item, patch_version))
                counts["items"] += 1
            except Exception as e:
                log.warning("item skip %s: %s", item.get("apiName"), e)

    return counts
