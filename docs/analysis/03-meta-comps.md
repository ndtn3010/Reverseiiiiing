# TFT — Meta Comps (Set 18 · Patch 18.4)

> Snapshot 2026-10-19. Rankings disagree across sources — confidence = source agreement count. Re-scrape before shipping; comp meta drifts daily.

---

## 1. Tier Overview

| Comp | Carry | Playstyle | Confidence | Avg Place |
|------|-------|-----------|------------|-----------|
| Solar Kayle Reroll | Kayle (4c) | Reroll @ 6–7 | **S** (3 sources) | — |
| Solar Rapidfire Reroll | 1c rerolls | Reroll @ 6 | **S** (36.3% play rate, Blitz) | — |
| Executioner Azir | Azir (5c) | Fast 8/9 | **S+** (SeeMeta #1 played) | **4.09** |
| Flora Fatalis Azir | Azir (5c) | Fast 8 | **S** | **4.20** |
| Defender Rengar | Rengar | Standard 8 | **S** (Emblem #1) | **4.14** |
| Riftbeast Elder Dragon | Elder Dragon (5c) | Fast 8→9 | **S** | — |
| Elderwood Draven | Draven | Fast 9 | **A+** | — |
| Lunar Nidalee | Nidalee | Fast 8 | **A** | — |
| Juggernaut Elder Dragon | Elder Dragon frontline | Fast 8 | **A** | — |
| Spellweaver Rammus | Rammus | Standard | **A** | — |
| Kha'Zix Reroll | Kha'Zix (3c) | 3-cost reroll | **A** | — |
| Dark Ritual Reroll (Elise) | Elise | Reroll w/ Radiant Stoneplate | **A** (set-top on La Casita) | — |

---

## 2. Comp Profiles

### 2.1 Solar Kayle Reroll — S

| Field | Value |
|-------|-------|
| **Carry** | Kayle (4-cost) |
| **Playstyle** | Reroll at level 6 or 7 to 3-star Kayle, then level 8 for cap |
| **Core traits** | Solar (3+), Rapidfire or Executioner support |
| **BIS items** | Guinsoo's Rageblade → Jeweled Gauntlet → Rabadon's Deathcap / Hextech Gunblade |
| **Frontline items** | Gargoyle Stoneplate |
| **Econ** | Slow-roll at 50g on 6/7; level 8 after Kayle 3★ |
| **Threats to it** | Fast-9 Draven, Executioner Azir with Shojin |

### 2.2 Executioner Azir — S+

| Field | Value |
|-------|-------|
| **Carry** | Azir (5-cost) |
| **Playstyle** | Fast 8 at ~4-2, bleed to 9 |
| **Core traits** | Executioner (bonus crit scaling), supporting Spellweaver/Lunar |
| **BIS items** | Giant Slayer / Guinsoo's Rageblade / Jeweled Gauntlet · Spear of Shojin variants |
| **Econ** | Hold econ to 50g through 3-x, level 8 at 4-2, roll down |
| **Avg place** | 4.09 (~21k ranked games, SeeMeta) |

### 2.3 Flora Fatalis Azir — S

Same carry as Executioner Azir, different trait shell.

| Field | Value |
|-------|-------|
| **BIS items** | Spear of Shojin / Guinsoo's Rageblade / Jeweled Gauntlet |
| **Playstyle** | Fast 8 |
| **Avg place** | 4.20 (~103k lobbies, Emblem) |

### 2.4 Defender Rengar — S

| Field | Value |
|-------|-------|
| **Carry** | Rengar |
| **Playstyle** | Standard 8 (level 8 by ~4-5, stabilize) |
| **BIS items** | Infinity Edge / Jeweled Gauntlet / Bloodthirster |
| **Trait shell** | Defender frontline, assassin backline positioning |
| **Avg place** | 4.14 (~10.8k games, Emblem) |

### 2.5 Riftbeast Elder Dragon — S

| Field | Value |
|-------|-------|
| **Carry** | Elder Dragon (5-cost) |
| **Playstyle** | Fast 8 → push 9 for cap |
| **BIS items** | AP + tank hybrid on Dragon; itemized Riftbeast frontline |
| **Econ** | Interest cap through 3-x, roll on 8 for Dragon |

### 2.6 Elderwood Draven — A+

| Field | Value |
|-------|-------|
| **Carry** | Draven |
| **Playstyle** | **Fast 9** — play strong 5–6, bleed HP, hit level 9, roll for 5-cost cap |
| **BIS items** | Infinity Edge / Last Whisper / Bloodthirster or Jeweled Gauntlet |
| **Trait shell** | Elderwood 7+ (plants on board as extra entities) |

### 2.7 Kha'Zix Reroll — A

| Field | Value |
|-------|-------|
| **Carry** | Kha'Zix (3-cost) |
| **Playstyle** | 3-cost reroll at level 7 |
| **BIS items** | Infinity Edge / Hand of Justice / Bloodthirster |
| **Econ** | Hit 50g, slow-roll 7 |

### 2.8 Dark Ritual Reroll (Elise) — A

| Field | Value |
|-------|-------|
| **Carry** | Elise |
| **Playstyle** | Reroll with **Radiant Gargoyle Stoneplate** as the enabler |
| **BIS items** | AP + Gargoyle Stoneplate (Radiant) |
| **Note** | Set-top on La Casita del TFT 2026-10-18 |

---

## 3. Playstyle Taxonomy (for the engine)

The engine's comp matcher classifies state → playstyle to drive econ decisions:

| Playstyle | Level pivot | Econ pattern | Example comps |
|-----------|-------------|--------------|---------------|
| **1-cost reroll** | Stay 6, slow-roll 50g | Preserve streak, roll @ 50g | Solar Rapidfire Reroll |
| **3-cost reroll** | Push 7, slow-roll 50g | Econ to 50g, roll on 7 | Kha'Zix, Solar Kayle |
| **Standard 8** | Level 8 by 4-5 | Interest cap through 3-x | Defender Rengar, Spellweaver Rammus |
| **Fast 8** | Level 8 at 4-1 or 4-2 | Push XP aggressively, bleed HP | Executioner Azir, Flora Azir, Elder Dragon |
| **Fast 9** | Level 9 as early as possible | Max XP buy, play strong board | Elderwood Draven |

---

## 4. Comp Matcher — Engine Hooks

Each comp becomes a record:

```python
@dataclass
class Comp:
    id: str
    tier: str                      # S+, S, A+, A, B
    carries: list[str]
    required_traits: list[tuple[str, int]]   # (trait_id, breakpoint)
    items_bis: dict[str, list[str]]          # champ_id → [item_id, ...]
    playstyle: Playstyle
    level_pivot: int               # which level the comp pivots on
    boards: dict[int, list[str]]   # level → champ list (6, 8, 9)
    avg_place: float | None
    play_rate: float | None
    threats: list[str]             # comp ids that counter this
    source_count: int              # how many trackers list this
```

**Matcher score** (current state → comp fit):

```
fit = (shared_units × 1.0)
    + (shared_traits × 0.8)
    + (bis_items_available × 1.2)
    - (transition_cost × 0.5)
    - (contest_level × 0.6)        # from pool_state
```

Top-3 comps returned, UI shows them with transition cost.

---

## 5. Confidence & Refresh

| Comp | SeeMeta | Blitz | Mobalytics | Emblem | BunnyMuffins | La Casita |
|------|---------|-------|------------|--------|--------------|-----------|
| Solar Kayle Reroll | ✓ | ✓ | ✓ | — | — | — |
| Solar Rapidfire Reroll | ✓ | ✓ | ✓ | — | — | — |
| Executioner Azir | ✓ (S+) | — | — | — | — | — |
| Flora Fatalis Azir | — | — | — | ✓ | — | — |
| Defender Rengar | — | — | — | ✓ (#1) | — | — |
| Riftbeast Elder Dragon | ✓ | ✓ | — | ✓ | — | — |
| Elderwood Draven | — | ✓ | — | — | ✓ | — |
| Kha'Zix Reroll | — | — | — | — | ✓ | — |
| Dark Ritual Elise | — | — | — | — | — | ✓ (top) |

Multi-source presence = higher confidence weight in the engine. Daily re-scrape required; placement averages shift fast.
