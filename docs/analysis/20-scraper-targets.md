# TFT — Scraper Target Endpoints

> Nơi engine's scraper phải trỏ tới để pull full catalogs. CommunityDragon là nguồn chính — **không auth, không rate limit**.

---

## 1. CommunityDragon (nguồn chính)

### Base URL
```
https://raw.communitydragon.org/latest/
```

### Key paths
| Resource | Path |
|----------|------|
| **TFT data folder** | `/cdragon/tft/` |
| **Current patch TFT JSON** | `/cdragon/tft/en_us.json` |
| **Per-language** | `/cdragon/tft/<locale>.json` (en_us, vi_vn, etc.) |
| **Champion portraits** | `/game/assets/characters/tft18_<name>/hud/` |
| **Game client raw export** | `/game/` |

### Properties
- **Không auth required**
- **Không rate limit**
- **Không API key**
- Updated gần real-time khi Riot patch

### Example scraper call
```python
import httpx

CDRAGON_BASE = "https://raw.communitydragon.org/latest/cdragon/tft"

async def pull_tft_data():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{CDRAGON_BASE}/en_us.json")
        data = resp.json()
        return {
            "champions": data["sets"]["18"]["champions"],
            "traits": data["sets"]["18"]["traits"],
            "items": data["items"],
        }
```

---

## 2. Riot Developer API (cần key)

### Key endpoints
| Endpoint | Purpose |
|----------|---------|
| `https://ddragon.leagueoflegends.com/api/versions.json` | List tất cả patch versions |
| `https://developer.riotgames.com/apis#tft-static-data-v1` | Official TFT static data (cần key) |
| `https://<region>.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids` | Match history (cần key) |
| `https://<region>.api.riotgames.com/tft/league/v1/entries/{tier}/{division}` | Ladder standings |

### Rate limits (dev key)
- **20 req/second**
- **100 req/2 minutes**
- Production key: higher (negotiated)

### Headers
```
X-Riot-Token: <API_KEY>
```

---

## 3. Patch version detection

```python
async def detect_current_patch() -> str:
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    resp = await httpx.get(url)
    versions = resp.json()
    return versions[0]   # "18.5.1" format
```

TFT patch versions **match LoL patch versions**.

**Alternative** (CDragon, no auth):
```python
async def detect_patch_from_cdragon() -> str:
    url = "https://raw.communitydragon.org/latest/content-metadata.json"
    resp = await httpx.get(url)
    return resp.json()["version"]
```

**Patch day detection**: hash CDragon TFT JSON blob. New hash = new patch.

---

## 4. Meta comp scrape targets

| Site | URL pattern | What |
|------|-------------|------|
| **SeeMeta** | `https://seemeta.com/en/tft/set-18/best-comps` | Current tier list |
| **SeeMeta** | `https://seemeta.com/en/tft/set-18/augments` | Full augment catalog |
| **SeeMeta** | `https://seemeta.com/en/tft/set-18/items` | Full item/wisp catalog |
| **SeeMeta** | `https://seemeta.com/en/tft/set-18/patch-notes` | Patch notes aggregator |
| **Metabot** | `https://metabot.gg/en/TFT/18/augments` | Augment tier list |
| **Metabot** | `https://metabot.gg/en/TFT/18/items/cheat-sheet` | Item cheat sheet |
| **Metabot** | `https://metabot.gg/en/TFT/18/items/radiant` | Radiant tier list |
| **Mobalytics** | `https://mobalytics.gg/tft/set18/items/combined` | Combined items + components |
| **MetaSrc** | `https://www.metasrc.com/tft/stats/champions` | Champion win rates |
| **Blitz** | `https://blitz.gg/tft/comps` | Comp tier list |
| **BunnyMuffins** | `https://bunnymuffins.lol/meta/` | Challenger opinion |
| **TFT Flow** | `https://tftflow.com/tier-list` | Alternative tier list |
| **TFT Academy** | `https://tftacademy.com/tierlist/comps/` | Comp build guides |
| **Emblem Comp** | `https://emblemcomp.gg/meta-report` | Statistical meta report |

### Scrape strategy
- Mỗi site: HTML parse với BeautifulSoup
- Cross-check tier giữa ≥3 sites để tính confidence
- Daily refresh (comp tier shifts fast)
- Patch day → force refresh toàn bộ

---

## 5. Riot official patch notes

```
https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-<ver>/
```

Example: `teamfight-tactics-patch-18-5/`

### Parse strategy
- RSS/Atom feed (nếu có) cho auto-detect
- HTML parse structured sections: Trait Updates / Champion Updates / Augment Updates / Wisp Updates
- Fallback: text diff vs previous patch

---

## 6. Community scraper libraries

| Lib | Lang | Purpose |
|-----|------|---------|
| **tft-oracle** | npm | CDragon reader, auto-refresh |
| **TFT_DDragon** (InFinity54) | GitHub mirror | Static data mirror |
| **tft-assets** (ngocleek) | GitHub | Portrait/trait icon assets |

→ Code đáng đọc để biết exact CDragon file paths.

---

## 7. Scraper priority list

### Phase 1 (foundation)
1. CDragon JSON blob (champions + traits + items)
2. Patch version detection
3. Riot patch notes HTML parse

### Phase 2 (meta)
4. SeeMeta comp list (primary)
5. Mobalytics comp list (cross-check)
6. Metabot augment catalog
7. Metabot item cheat sheet
8. MetaSrc champion stats

### Phase 3 (dynamic)
9. Daily tier refresh across 5+ sites
10. B-patch detection via RSS

---

## 8. Engine scheduler config

```yaml
# config/scraper.yaml
sources:
  - name: cdragon_tft
    url: https://raw.communitydragon.org/latest/cdragon/tft/en_us.json
    cron: "0 */6 * * *"           # 6h
    on_change: full_refresh

  - name: riot_versions
    url: https://ddragon.leagueoflegends.com/api/versions.json
    cron: "*/15 * * * *"          # 15min
    on_change: trigger_patch_workflow

  - name: riot_patch_notes
    url_pattern: https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-{ver}/
    cron: "*/30 * * * *"          # 30min
    on_detect: parse_and_delta

  - name: seemeta_comps
    url: https://seemeta.com/en/tft/set-18/best-comps
    cron: "0 2,14 * * *"          # 2x daily
    confidence_weight: 1.0

  - name: metabot_augments
    url: https://metabot.gg/en/TFT/18/augments
    cron: "0 2 * * *"             # 1x daily
    confidence_weight: 1.0

  - name: mobalytics_comps
    url: https://mobalytics.gg/tft/set18/tier-list
    cron: "0 2 * * *"
    confidence_weight: 0.8

  - name: metasrc_champions
    url: https://www.metasrc.com/tft/stats/champions
    cron: "0 2 * * *"
    confidence_weight: 0.9
```

---

## 9. SQLite schema (initial)

```sql
CREATE TABLE patches (
    version TEXT PRIMARY KEY,
    release_date TEXT NOT NULL,
    cdragon_hash TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE champions (
    champ_id TEXT PRIMARY KEY,
    set_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    cost INTEGER NOT NULL,
    hp_1star INTEGER, ad_1star INTEGER, armor INTEGER, mr INTEGER,
    as_base REAL, range INTEGER, mana_start INTEGER, mana_max INTEGER,
    ability_json TEXT,     -- blob của ability data
    traits_json TEXT,
    patch_version TEXT REFERENCES patches(version)
);

CREATE TABLE traits (
    trait_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    breakpoints_json TEXT NOT NULL,    -- [3, 5, 7, 9, 11]
    effects_json TEXT NOT NULL,         -- {bp: effect_desc}
    champions_json TEXT NOT NULL
);

CREATE TABLE items (
    item_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    recipe TEXT,                        -- "BF+Gloves"
    stats_json TEXT NOT NULL,
    effect_description TEXT,
    is_radiant INTEGER DEFAULT 0,
    is_ornn INTEGER DEFAULT 0,
    is_emblem INTEGER DEFAULT 0,
    unique_flag INTEGER DEFAULT 1
);

CREATE TABLE augments (
    augment_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tier TEXT NOT NULL,                 -- silver/gold/prismatic
    category TEXT,                      -- combat/econ/trait/hero/scaling/risk
    effect_description TEXT,
    patch_added TEXT,
    disabled INTEGER DEFAULT 0,
    tier_rating TEXT                    -- S+/S/A+/A/B/C (scraped daily)
);

CREATE TABLE wisps (
    wisp_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,             -- combat/economy/shop/items/champion/risky/misc
    price INTEGER,
    effect_description TEXT,
    patch_added TEXT
);

CREATE TABLE comps (
    comp_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    primary_carry TEXT NOT NULL,
    required_traits_json TEXT NOT NULL,
    bis_items_json TEXT NOT NULL,
    playstyle TEXT,                     -- 1c_reroll/3c_reroll/fast_8/fast_9/standard
    level_pivot INTEGER,
    tier_rating TEXT,
    avg_place REAL,
    play_rate REAL,
    source_count INTEGER DEFAULT 1,
    last_updated TIMESTAMP
);

CREATE TABLE encounters (
    encounter_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    effect_description TEXT,
    fire_phase TEXT                     -- game_start/stage_3_3/last_augment/per_phase
);

CREATE INDEX idx_comp_tier ON comps(tier_rating);
CREATE INDEX idx_champ_cost ON champions(cost);
CREATE INDEX idx_augment_tier ON augments(tier, tier_rating);
```
