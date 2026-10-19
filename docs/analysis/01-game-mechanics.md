# TFT — Game Mechanics (Analysis)

> Target: foundation knowledge the AI must model before any decision logic.
> Set 18 (Enchanted Wilds) · Patch 18.4 · Research date 2026-10-19.

---

## 1. Match Structure

A TFT match is 8 players, elimination by HP = 0. Match is a sequence of **stages**, each stage a cluster of **rounds**.

### 1.1 Round types per stage

| Round ID | Type | Notes |
|----------|------|-------|
| `X-1` | PvE (Stage 1) / PvP | Stage 1 only has PvE |
| `X-2` | PvP | — |
| `X-3` | PvP | — |
| `X-4` | **Carousel** | Rotating platform of champs holding items; lowest HP picks first |
| `X-5` | PvP | — |
| `X-6` | PvP | — |
| `X-7` | PvE | Minion wave or neutral camp (krugs/wolves/raptors analogue) |

Stage 1 has only 3 PvE rounds (`1-1`, `1-2`, `1-3`) seeding gold/XP/components.

### 1.2 Augment Armories

Fixed stages, standard order:
- **2-1** → Silver augment choice
- **3-2** → Gold augment choice
- **4-2** → Prismatic augment choice

Each armory offers 3 options, up to 3 rerolls. Tier mix drifts (Silver ↓, Prismatic ↑) if portals skew.

---

## 2. Economy

### 2.1 Income per round

| Source | Amount |
|--------|--------|
| Base income | 5g/round (ramped 2/2/3/4/5 in Stage 1-x) |
| Interest | +1g per 10g banked, **capped at 5g** (at 50g) |
| Win streak | +1g @ 2/3/4 wins, +2g @ 5, +3g @ 6+ |
| Loss streak | symmetric with win streak |
| Round win | +1g (base PvP win) |

**Interest break: hoard to 50g ASAP** — the +5g compounds across every round until spent.

### 2.2 Spending

| Action | Cost |
|--------|------|
| Reroll shop | 2g |
| Buy XP (4 XP) | 4g |
| End-of-round free XP | 2 XP (automatic) |

### 2.3 Interest tier table (reference)

| Bank | Interest |
|------|----------|
| 0–9 | 0 |
| 10–19 | +1 |
| 20–29 | +2 |
| 30–39 | +3 |
| 40–49 | +4 |
| **50+** | **+5** (cap) |

---

## 3. Levels & XP

Level determines **board size** and **shop odds**. XP buy = 4g for 4 XP.

| Level | XP to next | Board slots |
|-------|------------|-------------|
| 1 | 2 | 1 |
| 2 | 2 | 2 |
| 3 | 6 | 3 |
| 4 | 10 | 4 |
| 5 | 20 | 5 |
| 6 | 36 | 6 |
| 7 | 48 | 7 |
| 8 | 76 | 8 |
| 9 | 84 | 9 |
| 10 | 100 | 10 |
| 11 | — | 11 |

---

## 4. Shop Odds (Set 18)

Each shop refresh = **5 independent slots**, each rolled per the table below. Pool-shared across lobby.

| Lvl | 1-cost | 2-cost | 3-cost | 4-cost | 5-cost |
|-----|--------|--------|--------|--------|--------|
| 1 | 100 | 0 | 0 | 0 | 0 |
| 2 | 100 | 0 | 0 | 0 | 0 |
| 3 | 75 | 25 | 0 | 0 | 0 |
| 4 | 55 | 30 | 15 | 0 | 0 |
| 5 | 45 | 33 | 20 | 2 | 0 |
| 6 | 30 | 40 | 25 | 5 | 0 |
| 7 | 19 | 30 | **43** | 8 | 0 |
| 8 | 15 | 20 | 32 | **30** | 3 |
| 9 | 10 | 15 | 25 | 35 | 15 |
| 10 | 5 | 10 | 20 | 40 | 25 |
| 11 | 1 | 2 | 12 | **50** | **35** |

Reading:
- **Level 7** = 3-cost reroll peak (43%)
- **Level 8** = 4-cost roll-down peak (30%)
- **Level 11** = legendary hunting (35% 5-costs)

---

## 5. Champion Pool

Pool is **shared across all 8 players**. Opponent copies on their boards subtract from your hit chance.

| Cost | Copies/champ | Distinct champs | Total pool |
|------|--------------|-----------------|------------|
| 1 | 30 | 14 | 420 |
| 2 | 25 | 13 | 325 |
| 3 | 18 | 14 | 252 |
| 4 | 10 | 14 | 140 |
| 5 | 9 | 10 | 90 |

**Hit probability for a specific champ at level L** with `k` remaining in pool, `n` total in pool at that cost, odds `p` for that cost tier:

```
P(hit per slot) = p × (k / N_total_at_cost_remaining)
P(hit per shop) = 1 − (1 − P_per_slot)^5
```

Memory read gives us `k` directly (pool state is in memory). Vision mode has to estimate from visible opponent boards.

---

## 6. Items

### 6.1 Components (9)

| Component | Primary stat |
|-----------|--------------|
| B.F. Sword | +10 AD |
| Recurve Bow | +10% AS |
| Needlessly Large Rod | +10 AP |
| Tear of the Goddess | +15 mana |
| Chain Vest | +20 armor |
| Negatron Cloak | +20 MR |
| Giant's Belt | +150 HP |
| Sparring Gloves | +5% crit, +5% dodge |
| Spatula | emblem base |

### 6.2 Completed items

9×9 standard combine matrix = 36 unique completed items + 10 Spatula-emblem items. Load from Riot static data at startup; don't hardcode.

### 6.3 Variants

Radiant / Ornn artifacts / support items — patch-driven lookup. Treat as a dynamic table.

---

## 7. Set 18 Mechanics — Enchanted Wilds

### 7.1 Wisps (headline mechanic)

Single-use purchases that appear in the **rightmost shop slot** every other round. Planning-phase only.

| Category | Effect family |
|----------|---------------|
| Combat | buff this fight only |
| Economy | gold or XP |
| Shop | reroll / odds manipulation |
| Items | components or completed |
| Champions | free units |
| Risk/Reward | gamble effects |

**After Stage 5**, every alternate Wisp slot is guaranteed Combat tier → late-game variance tightens.

**Blossom trait** interacts directly with Wisps:
- **3** → Wisps upgraded
- **5** → Wisps in every shop
- **7** → gold on Wisp purchase
- **9** → buy 2 Wisps/round
- **11** → Wisps overflow

### 7.2 Other set traits (highlights)

| Trait | Breakpoints | Mechanic |
|-------|-------------|----------|
| Elderwood | 3/5/7/9/11 | Spawns **plants** as board entities |
| Fae | — | Attracts **Pixies** (companion units) |
| Solar / Lunar | — | Pair unlocks hidden **Eclipse** |
| Blackthorn | 2/4/6 | Sacrifices ally on Blackthorn hex pre-combat for buff |
| Brawler | 2/4/6 | Team max HP, Brawlers more |
| Rapidfire | 2/3/4/5 | Attack speed |

Signature traits (single-champ) on Ivern, Maokai, Zyra.

### 7.3 Encounters & Portals

Both return in Set 18. Encounter specifics are patch-variable — expose an `encounter_event` field in game state, don't hardcode outcomes.

---

## 8. State Schema (what the AI tracks)

```python
@dataclass
class GameState:
    # match-level
    patch: str                       # "18.4"
    round: str                       # "3-2"
    stage: int
    phase: Phase                     # planning | combat | carousel | pve
    encounter_event: str | None

    # self
    gold: int
    level: int
    xp: tuple[int, int]              # current, needed
    hp: int
    streak: int                      # signed (+win / -loss)
    bench: list[Unit]
    board: list[BoardSlot]           # hex coords (q, r)
    shop: list[ShopSlot]
    shop_locked: bool
    wisp_slot: Wisp | None           # rightmost shop slot when active
    augments: list[Augment]
    components: list[Component]
    traits_active: dict[str, int]

    # lobby
    opponents: dict[int, OpponentState]  # id → state (memory: all live; vision: last-scouted)
    pool_state: dict[str, int]           # champ_id → copies left in global pool

    # pairings
    next_opponent: int | None
```

---

## 9. Decision Points the Engine Must Answer

| Phase | Question |
|-------|----------|
| Carousel | Which champ+item combo to grab (based on current comp fit + econ) |
| Shop (every round) | For each slot: buy / skip. Lock? |
| Shop | Reroll? (gold vs threshold, hit probability vs need) |
| Level | Buy XP now, or hoard for roll-down? |
| Positioning | Frontline/backline rotation vs scouted next opponent |
| Items | Which component slams, which to hold for BIS |
| Wisp | Buy / skip the active Wisp slot |
| Augment | Pick from 3 offered (comp fit × tier × scaling curve) |

Each becomes a function in `src/engine/` that consumes `GameState` and the meta DB.
