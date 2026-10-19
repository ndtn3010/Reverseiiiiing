# TFT — Current Patch (Set 18, Patch 18.4)

> Research date 2026-10-19. Values drift between patches — the live scraper is source of truth; this doc is a snapshot.

---

## 1. Set & Patch Overview

| Field | Value |
|-------|-------|
| Set | **Set 18 — Enchanted Wilds** |
| Live patch | **18.4** (B-patch applied 2026-10-08) |
| Next patch | **18.5** — scheduled 2026-10-21 |
| End-of-set patch | 18.6 |
| Next set start | **Patch 19.1 — 2026-12-01** |
| Theme | Nature / fey / woodland — Elderwood, Fae, Blossom, Blackthorn, Solar / Lunar / Eclipse |
| Scale | ~65 champions, ~35 traits |

**AI implication**: Set 19 drops in ~6 weeks. All meta data has a hard expiry on **2026-12-01** — the scraper needs a set-change detector that invalidates comp DB wholesale, not just incremental patch deltas.

---

## 2. Patch 18.4 — What Changed

### 2.1 Design direction
Riot shifted **power from traits → individual units**. Swingy champions got consistency buffs. No roster or breakpoint changes.

### 2.2 Numbers
- ~22 champions retuned
- 3 cashout engines trimmed (trait anvils / Wisp cashouts)
- 7 units buffed in B-patch (2026-10-08)
- 8 Wisps + 10 augments adjusted
- 1 augment disabled: **Heart of Steel** (bug)
- 3 arenas disabled (bug)

### 2.3 Patch cadence
- PC gets changes first
- Mobile parity lags a few days
- B-patches are hotfix-only; expect augment/wisp emergency nerfs mid-patch

---

## 3. Patch Watcher Requirements

The scraper module needs to track:

| Signal | Source | Trigger |
|--------|--------|---------|
| New patch version | Riot static data hash | Full data refresh |
| B-patch applied | Riot patch notes RSS | Delta refresh (augments, wisps) |
| Disabled augments/arenas | Patch notes parse | Blacklist update |
| Set rollover (19.1) | Riot calendar / set reveal page | Wipe comp DB, rebuild from scratch |

**18.5 preview**: ~82 numeric changes queued (datamined, unofficial). Do not treat as live until Riot publishes notes on 2026-10-21.

---

## 4. Meta Data Volatility

Which fields change per patch and must be re-scraped:

| Field | Volatility | Refresh cadence |
|-------|------------|-----------------|
| Champion stats (HP, AD, AP, mana) | High | Every patch |
| Trait breakpoints + effects | Low (18.4: zero changes) | Every patch (verify) |
| Augment pool + numbers | High | Every patch + B-patch |
| Wisp pool | High | Every patch + B-patch |
| Comp tier list | **Very high** | Daily (meta drift) |
| Item BIS per carry | High | Every patch |
| Shop odds table | Set-level | Set rollover only |
| Pool sizes | Set-level | Set rollover only |
| XP curve | Set-level | Set rollover only |

---

## 5. Scheduled Jobs the AI Needs

```yaml
# config/schedule.yaml
jobs:
  - name: riot_static_data
    cron: "0 */6 * * *"       # every 6h
    on_change: full_refresh

  - name: patch_notes_rss
    cron: "*/15 * * * *"      # every 15min
    on_change: trigger_delta_refresh

  - name: meta_comps_scrape
    cron: "0 2,14 * * *"      # twice daily
    sources: [metatft, mobalytics, tftacademy, seemeta, emblemcomp]

  - name: set_rollover_check
    cron: "0 0 * * *"         # daily
    target_date: 2026-12-01
    on_fire: wipe_comp_db_and_resync
```
