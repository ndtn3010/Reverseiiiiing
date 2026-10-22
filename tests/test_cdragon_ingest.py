"""Verify ingest logic works against a representative CDragon payload fixture."""

from pathlib import Path

from reverseiiiiing.meta import cdragon, db as dbmod


FIXTURE = {
    "setData": [
        {
            "mutator": "TFTSet18",
            "number": 18,
            "name": "Enchanted Wilds",
            "champions": [
                {
                    "apiName": "TFT18_Azir",
                    "name": "Azir",
                    "cost": 5,
                    "stats": {
                        "hp": 650,
                        "damage": 30,
                        "armor": 35,
                        "magicResist": 35,
                        "attackSpeed": 0.75,
                        "range": 4,
                        "critChance": 0.25,
                        "initialMana": 0,
                        "mana": 35,
                    },
                    "ability": {
                        "name": "Arise!",
                        "desc": "+150% AS, next 6 soldier commands",
                        "variables": [{"name": "Damage", "value": [43, 65, 105]}],
                    },
                    "traits": ["TFT18_Executioner", "TFT18_FloraFatalis"],
                },
                {
                    "apiName": "TFT18_Kayle",
                    "name": "Kayle",
                    "cost": 4,
                    "stats": {
                        "hp": 550,
                        "damage": 45,
                        "armor": 30,
                        "magicResist": 30,
                        "attackSpeed": 0.70,
                        "range": 4,
                    },
                    "ability": {"name": "Solar Judgment", "desc": "on-hit magic"},
                    "traits": ["TFT18_Solar", "TFT18_Rapidfire"],
                },
            ],
            "traits": [
                {
                    "apiName": "TFT18_Blossom",
                    "name": "Blossom",
                    "effects": [
                        {"minUnits": 3, "maxUnits": 4, "variables": {"bonus_ad": 0.12}},
                        {"minUnits": 5, "maxUnits": 6, "variables": {"bonus_ad": 0.30}},
                        {"minUnits": 7, "maxUnits": 8, "variables": {"bonus_ad": 0.40}},
                        {"minUnits": 9, "maxUnits": 10, "variables": {"bonus_ad": 0.50}},
                        {"minUnits": 11, "maxUnits": 25000, "variables": {"bonus_ad": 1.00}},
                    ],
                },
            ],
        }
    ],
    "items": [
        {
            "apiName": "TFT_Item_InfinityEdge",
            "name": "Infinity Edge",
            "composition": ["TFT_Item_BFSword", "TFT_Item_SparringGloves"],
            "effects": {"CritChance": 0.35, "AD": 0.35},
            "desc": "Convert crit damage to true damage",
            "unique": True,
        },
        {
            "apiName": "TFT_Item_RadiantInfinityEdge",
            "name": "Radiant Infinity Edge",
            "effects": {"CritChance": 0.75, "AD": 0.75},
            "desc": "Radiant variant",
            "unique": True,
        },
    ],
}


def test_ingest_populates_db(tmp_path: Path):
    db_path = tmp_path / "test.db"
    dbmod.init_db(db_path)

    counts = cdragon.ingest(
        payload=FIXTURE,
        set_id=18,
        patch_version="18.5",
        cdragon_hash="deadbeef",
        db_path=str(db_path),
    )

    assert counts == {"champions": 2, "traits": 1, "items": 2}

    with dbmod.connect(db_path) as conn:
        azir = conn.execute(
            "SELECT * FROM champions WHERE champ_id = 'TFT18_Azir'"
        ).fetchone()
        assert azir is not None
        assert azir["name"] == "Azir"
        assert azir["cost"] == 5
        assert azir["hp_1star"] == 650
        assert azir["ad_1star"] == 30
        assert azir["mana_max"] == 35
        assert azir["range"] == 4

        blossom = conn.execute(
            "SELECT * FROM traits WHERE trait_id = 'TFT18_Blossom'"
        ).fetchone()
        assert blossom is not None
        import json
        bps = json.loads(blossom["breakpoints_json"])
        assert bps == [3, 5, 7, 9, 11]

        ie = conn.execute(
            "SELECT * FROM items WHERE item_id = 'TFT_Item_InfinityEdge'"
        ).fetchone()
        assert ie["recipe"] == "TFT_Item_BFSword+TFT_Item_SparringGloves"
        assert ie["is_radiant"] == 0

        radiant_ie = conn.execute(
            "SELECT * FROM items WHERE item_id = 'TFT_Item_RadiantInfinityEdge'"
        ).fetchone()
        assert radiant_ie["is_radiant"] == 1

        patch = conn.execute(
            "SELECT * FROM patches WHERE version = '18.5'"
        ).fetchone()
        assert patch["cdragon_hash"] == "deadbeef"


def test_upsert_overwrites(tmp_path: Path):
    """Second ingest with same ids updates rather than erroring."""
    db_path = tmp_path / "test.db"
    dbmod.init_db(db_path)
    cdragon.ingest(FIXTURE, 18, "18.5", "hash1", str(db_path))

    fixture2 = {
        "setData": [{
            "number": 18,
            "champions": [{
                "apiName": "TFT18_Azir",
                "name": "Azir",
                "cost": 5,
                "stats": {"hp": 700, "damage": 32, "armor": 35, "magicResist": 35,
                          "attackSpeed": 0.75, "range": 4, "initialMana": 0, "mana": 40},
                "ability": {},
                "traits": [],
            }],
            "traits": [],
        }],
        "items": [],
    }
    cdragon.ingest(fixture2, 18, "18.6", "hash2", str(db_path))

    with dbmod.connect(db_path) as conn:
        azir = conn.execute("SELECT hp_1star, mana_max, patch_version FROM champions "
                            "WHERE champ_id = 'TFT18_Azir'").fetchone()
        assert azir["hp_1star"] == 700
        assert azir["mana_max"] == 40
        assert azir["patch_version"] == "18.6"
