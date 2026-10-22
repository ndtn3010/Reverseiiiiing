import json
import sqlite3
from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path
from typing import Iterator


SCHEMA_SQL = files("reverseiiiiing.meta").joinpath("schema.sql").read_text()


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str | Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def upsert_patch(conn: sqlite3.Connection, version: str, cdragon_hash: str | None = None,
                 release_date: str | None = None) -> None:
    conn.execute(
        """
        INSERT INTO patches (version, release_date, cdragon_hash)
        VALUES (?, ?, ?)
        ON CONFLICT(version) DO UPDATE SET
            cdragon_hash = COALESCE(excluded.cdragon_hash, patches.cdragon_hash),
            release_date = COALESCE(excluded.release_date, patches.release_date)
        """,
        (version, release_date, cdragon_hash),
    )


def upsert_champion(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute(
        """
        INSERT INTO champions (
            champ_id, set_id, name, cost,
            hp_1star, ad_1star, armor, mr, as_base, range,
            mana_start, mana_max, ability_json, traits_json, patch_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(champ_id) DO UPDATE SET
            name = excluded.name,
            cost = excluded.cost,
            hp_1star = excluded.hp_1star,
            ad_1star = excluded.ad_1star,
            armor = excluded.armor,
            mr = excluded.mr,
            as_base = excluded.as_base,
            range = excluded.range,
            mana_start = excluded.mana_start,
            mana_max = excluded.mana_max,
            ability_json = excluded.ability_json,
            traits_json = excluded.traits_json,
            patch_version = excluded.patch_version
        """,
        (
            row["champ_id"], row["set_id"], row["name"], row["cost"],
            row.get("hp_1star"), row.get("ad_1star"), row.get("armor"),
            row.get("mr"), row.get("as_base"), row.get("range"),
            row.get("mana_start"), row.get("mana_max"),
            json.dumps(row.get("ability", {})),
            json.dumps(row.get("traits", [])),
            row.get("patch_version"),
        ),
    )


def upsert_trait(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute(
        """
        INSERT INTO traits (
            trait_id, set_id, name, breakpoints_json, effects_json,
            champions_json, patch_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(trait_id) DO UPDATE SET
            name = excluded.name,
            breakpoints_json = excluded.breakpoints_json,
            effects_json = excluded.effects_json,
            champions_json = excluded.champions_json,
            patch_version = excluded.patch_version
        """,
        (
            row["trait_id"], row["set_id"], row["name"],
            json.dumps(row.get("breakpoints", [])),
            json.dumps(row.get("effects", {})),
            json.dumps(row.get("champions", [])),
            row.get("patch_version"),
        ),
    )


def upsert_item(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute(
        """
        INSERT INTO items (
            item_id, name, recipe, stats_json, effect_description,
            is_radiant, is_ornn, is_emblem, unique_flag, patch_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(item_id) DO UPDATE SET
            name = excluded.name,
            recipe = excluded.recipe,
            stats_json = excluded.stats_json,
            effect_description = excluded.effect_description,
            is_radiant = excluded.is_radiant,
            is_ornn = excluded.is_ornn,
            is_emblem = excluded.is_emblem,
            unique_flag = excluded.unique_flag,
            patch_version = excluded.patch_version
        """,
        (
            row["item_id"], row["name"], row.get("recipe"),
            json.dumps(row.get("stats", {})),
            row.get("effect_description"),
            int(row.get("is_radiant", 0)),
            int(row.get("is_ornn", 0)),
            int(row.get("is_emblem", 0)),
            int(row.get("unique_flag", 1)),
            row.get("patch_version"),
        ),
    )


def counts(conn: sqlite3.Connection) -> dict[str, int]:
    tables = ["patches", "champions", "traits", "items", "augments", "wisps", "comps", "encounters"]
    out = {}
    for t in tables:
        out[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    return out
