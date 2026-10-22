PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS patches (
    version       TEXT PRIMARY KEY,
    release_date  TEXT,
    cdragon_hash  TEXT,
    detected_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS champions (
    champ_id       TEXT PRIMARY KEY,
    set_id         INTEGER NOT NULL,
    name           TEXT NOT NULL,
    cost           INTEGER NOT NULL,
    hp_1star       INTEGER,
    ad_1star       INTEGER,
    armor          INTEGER,
    mr             INTEGER,
    as_base        REAL,
    range          INTEGER,
    mana_start     INTEGER,
    mana_max       INTEGER,
    ability_json   TEXT,
    traits_json    TEXT,
    patch_version  TEXT,
    FOREIGN KEY (patch_version) REFERENCES patches(version)
);

CREATE INDEX IF NOT EXISTS idx_champ_cost ON champions(cost);
CREATE INDEX IF NOT EXISTS idx_champ_set ON champions(set_id);

CREATE TABLE IF NOT EXISTS traits (
    trait_id          TEXT PRIMARY KEY,
    set_id            INTEGER NOT NULL,
    name              TEXT NOT NULL,
    breakpoints_json  TEXT NOT NULL,
    effects_json      TEXT NOT NULL,
    champions_json    TEXT,
    patch_version     TEXT,
    FOREIGN KEY (patch_version) REFERENCES patches(version)
);

CREATE INDEX IF NOT EXISTS idx_trait_set ON traits(set_id);

CREATE TABLE IF NOT EXISTS items (
    item_id              TEXT PRIMARY KEY,
    name                 TEXT NOT NULL,
    recipe               TEXT,
    stats_json           TEXT NOT NULL,
    effect_description   TEXT,
    is_radiant           INTEGER DEFAULT 0,
    is_ornn              INTEGER DEFAULT 0,
    is_emblem            INTEGER DEFAULT 0,
    unique_flag          INTEGER DEFAULT 1,
    patch_version        TEXT,
    FOREIGN KEY (patch_version) REFERENCES patches(version)
);

CREATE TABLE IF NOT EXISTS augments (
    augment_id            TEXT PRIMARY KEY,
    name                  TEXT NOT NULL,
    tier                  TEXT NOT NULL,
    category              TEXT,
    effect_description    TEXT,
    patch_added           TEXT,
    disabled              INTEGER DEFAULT 0,
    tier_rating           TEXT,
    patch_version         TEXT,
    FOREIGN KEY (patch_version) REFERENCES patches(version)
);

CREATE INDEX IF NOT EXISTS idx_augment_tier ON augments(tier, tier_rating);

CREATE TABLE IF NOT EXISTS wisps (
    wisp_id             TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    category            TEXT NOT NULL,
    price               INTEGER,
    effect_description  TEXT,
    patch_added         TEXT,
    patch_version       TEXT,
    FOREIGN KEY (patch_version) REFERENCES patches(version)
);

CREATE TABLE IF NOT EXISTS comps (
    comp_id                TEXT PRIMARY KEY,
    name                   TEXT NOT NULL,
    primary_carry          TEXT NOT NULL,
    required_traits_json   TEXT NOT NULL,
    bis_items_json         TEXT NOT NULL,
    playstyle              TEXT,
    level_pivot            INTEGER,
    tier_rating            TEXT,
    avg_place              REAL,
    play_rate              REAL,
    source_count           INTEGER DEFAULT 1,
    last_updated           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_comp_tier ON comps(tier_rating);

CREATE TABLE IF NOT EXISTS encounters (
    encounter_id        TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    effect_description  TEXT,
    fire_phase          TEXT,
    set_id              INTEGER
);
