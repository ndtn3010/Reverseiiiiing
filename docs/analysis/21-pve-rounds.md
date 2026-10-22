# TFT — PvE Round Composition

> Minion waves, drops, no HP damage. Dùng cho opener planning + items planning.

---

## 1. Round-by-round table

| Round | Type | Content | Drop rule |
|-------|------|---------|-----------|
| **1-1** | PvE | 1 melee minion | Component + XP + 2g |
| **1-2** | PvE | 2–3 melee minions | Component + XP + 2g |
| **1-3** | PvE | 3–4 melee minions | Component + XP + 3g |
| **2-7** | PvE | **3 Krugs** | Guaranteed 1+ item HOẶC 5g |
| **3-7** | PvE | **1 Greater Murk Wolf + 4 Murk Wolves** | Guaranteed 1+ item HOẶC 5g |
| **4-7** | PvE | **1 Crimson Raptor + 4 Raptors** | Guaranteed 1+ item HOẶC 5g |
| **5-7** | PvE | **Dragon** | **Always drops items** |
| **6-7** | PvE | **Rift Herald** (nguồn khác: Elder Dragon) | Always drops items |
| **7-7+** | PvE | **Elder Dragon** | Always drops items |

**PvE rounds không gây HP damage.**

---

## 2. Set 18 minion data points

- **DA_Krug18** (Metabot entry) — stats scrape target
- Set 18 không confirm Krug/Wolf/Raptor stat changes vs base

---

## 3. Opener implications

### Carousel 1-4 priority (Stage 1)
- Pick best **component** (BF/Rod/Belt priority — xem [07-carousel-items.md](./07-carousel-items.md))
- Carousel champs = 1-cost (freshly minted, pool untouched)

### PvE drop expectations by stage
```
Stage 1 (1-1, 1-2, 1-3):  3 components + 7g + XP natural
Stage 2 Krug (2-7):        1-2 items/components + chance of orb
Stage 3 Wolf (3-7):        1-2 items + chance of orb
Stage 4 Raptor (4-7):      1-2 items + chance of orb
Stage 5+ Dragon:           Guaranteed items, usually completed/radiant
```

**Expected total components by 4-7**: ~8-10 (3 opener + 3 PvE drops avg + carousel grabs).

---

## 4. Engine simulation

```python
PVE_ROUNDS = {
    "1-1": {"type": "pve", "damage_dealt": 0, "drop_pool": "components_minor"},
    "1-2": {"type": "pve", "damage_dealt": 0, "drop_pool": "components_minor"},
    "1-3": {"type": "pve", "damage_dealt": 0, "drop_pool": "components_minor"},
    "2-7": {"type": "krugs", "damage_dealt": 0, "drop_pool": "stage_2_pve"},
    "3-7": {"type": "wolves", "damage_dealt": 0, "drop_pool": "stage_3_pve"},
    "4-7": {"type": "raptors", "damage_dealt": 0, "drop_pool": "stage_4_pve"},
    "5-7": {"type": "dragon", "damage_dealt": 0, "drop_pool": "guaranteed_items"},
    "6-7": {"type": "rift_herald", "damage_dealt": 0, "drop_pool": "guaranteed_items"},
    "7-7": {"type": "elder_dragon", "damage_dealt": 0, "drop_pool": "guaranteed_items"},
}

CAROUSEL_ROUNDS = ["1-4", "2-4", "3-4", "4-4", "5-4", "6-4", "7-4"]

def is_pve_round(round_id: str) -> bool:
    return round_id in PVE_ROUNDS

def is_carousel_round(round_id: str) -> bool:
    return round_id in CAROUSEL_ROUNDS

def expected_components_by_round(round_id: str) -> int:
    stage, rnd = parse_round(round_id)
    # ~3 từ stage 1 PvE, + ~1 per PvE round sau đó, + ~1 per carousel grab
    pve_passed = sum(1 for r in PVE_ROUNDS if round_before_or_equal(r, round_id))
    carousel_passed = sum(1 for r in CAROUSEL_ROUNDS if round_before_or_equal(r, round_id))
    return pve_passed + carousel_passed  # rough average
```
