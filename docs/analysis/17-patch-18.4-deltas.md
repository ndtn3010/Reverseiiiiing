# TFT — Patch 18.4 Exact Deltas

> B-patch 2026-10-08. Low-confidence (nguồn conflict) — engine phải scan live client tại patch deploy.

---

## 1. Patch philosophy

- Shift power **traits → individual units**
- ~22 champions retuned
- **0 roster changes**, **0 breakpoint changes**
- 3 cashout engines trimmed (trait anvils / Wisp cashouts)
- Pacing: combat arrival + departure phases −1s each (~1 phút saved/game)

---

## 2. Champions nerfed (18.4 vs 18.3)

| Champ | Change |
|-------|--------|
| **Diana** | Mana cost **30 → 40**. Damage line **305 → 230** (full: 75/115/180/305 → 75/115/180/230) |
| **Maokai** | Mana cost **90 → 100** |
| **Master Yi** | AD **62 → 60** (mana 90 → 100 ambiguous attribution) |
| **Ashe** | Nerfed (details not pulled) |

---

## 3. Champions buffed (B-patch 10-08)

**7 units buffed** — exact changes không surfaced đầy đủ. Verify client-side.

---

## 4. New Wisps (4 added)

| Wisp | Purpose |
|------|---------|
| **Drizzle** | — |
| **Grove Armor** | — |
| **Returning Friend** | — |
| **Room for a Shroom** | — |

→ Thêm 4 Wisps vào low-gold shops specifically.

---

## 5. Wisps adjusted

| Wisp | Change |
|------|--------|
| **Animate Shop** | Duration **26s → 24s** |
| **Combust** | Damage **22% → 18% max HP** |
| **Cutpurse** | Price **3g → 2g** |
| **Slow Study** | Price **4g → 2g** |
| **Search Party** | Price **3g/1g → 1g/0g** |
| **Polymorph Wisps** | Limited to **first 2s** of planning phase |

Mua Wisps không chặn lên level (18.2 change still active).

---

## 6. Augments

### New
- **Calculated Loss** — added

### Removed
- **Nesting Dolls** — removed

### Disabled (bug)
- **Heart of Steel** — disabled by B-patch

### Nerfed
- **Explosive Growth** — XP/round nerfed to **9**

**10 augments total adjusted** per B-patch (full list not surfaced).

---

## 7. Arenas

- **3 arenas disabled** (bug fixes)
- Names not pulled

---

## 8. Release timeline

| Event | Date |
|-------|------|
| 18.4 Live | **2026-10-07** |
| B-patch | **2026-10-08** |
| **18.5 scheduled** | **2026-10-21** |
| 18.6 (end-of-set) | ~2026-11-18 |
| **19.1 (next set start)** | **2026-12-01** |

---

## 9. 18.5 preview (datamined, UNOFFICIAL)

- **~82 numeric changes** queued
- Không treat là live cho tới khi Riot publish notes
- Engine phải wait patch notes RSS trigger

---

## 10. Engine refresh workflow

### Patch day (18.5 → 18.6)
```yaml
on_patch_detected:
  - fetch_riot_static_data()
  - fetch_patch_notes_rss()
  - diff_against_last_patch()
  - update_champion_db(diff.champions)
  - update_item_db(diff.items)
  - update_trait_db(diff.traits)
  - update_augment_db(diff.augments)
  - update_wisp_db(diff.wisps)
  - re_scrape_meta_comps()  # tier list sẽ shift
  - mark_comp_tier_dirty(all)  # recompute scoring
```

### B-patch day
```yaml
on_b_patch_detected:
  - fetch_patch_notes_rss()
  - partial_update(diff)   # chỉ augments/wisps/arenas
  - blacklist_disabled(diff.disabled)
  - re_scrape_meta_comps()
```

### Set rollover (19.1, 2026-12-01)
```yaml
on_set_rollover:
  - archive_set18_db()
  - wipe_comp_db()
  - wipe_augment_wisp_db()
  - fetch_full_set19_static_data()
  - rebuild_from_scratch()
  - alert_user("Set 19 detected — rebuilding knowledge base")
```

---

## 11. Confidence levels

| Data | Confidence | Source |
|------|-----------|--------|
| Pool sizes | **High** | SeeMeta × 2 sources |
| Shop odds | **High** | SeeMeta, Metabot, TopMeta |
| XP curve | **High** | Noxu, TFT Ninja, TFT Lab |
| Interest table | **High** | Multi-source agreement |
| Streak table | **Medium** | 2 variants in circulation |
| End-of-round damage | **Medium** | TFT Ninja vs TFTips disagree stage 3-4 |
| Champion ability values | **Medium** | SeeMeta reverse-engineered, 18.3 version |
| Trait exact numbers | **Medium** | Wiki vs tft.tools disagree Blossom 9 |
| 18.4 B-patch deltas | **Low** | Mobafire count ≠ SeeMeta diff |
| Mortdog philosophy | **Low** | No 2026 interview surfaced |
| Round timer (seconds) | **Low** | Convention 30s, not Set 18 confirmed |

→ Engine design: **everything numeric comes from live scrape**, docs là reference cho structure và decision logic, không phải hardcode truth.
