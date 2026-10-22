# TFT — Set 18 Encounters

> Encounter = effect chọn tại game start, affect **whole lobby**. Thay thế Portal mechanic của Set 10.

---

## 1. Confirmed Set 18 encounters

| Encounter | Hiệu ứng |
|-----------|---------|
| **Kayle** | Free rerolls each phase |
| **Ashe** | XP cost per level **−2** |
| **Draven** | Last 2 living players get **70g each** |
| **Teemo** | +1 extra optimization reroll |
| **Karma** | Last optimization is **Prismatic** |
| **Kobuko** | Gold each phase |
| **Ornn** | Items + reforgers at **3-3** |
| **Lux** | **3 random emblems** |
| **Yunara** | Completed-item anvil at start |
| **Vi** | 2 component anvils |

---

## 2. Removed in Set 18

- Loot Subscription
- Artifact Anvil
- Reroll Start

---

## 3. Also referenced (uncertain)

- Completed Item Anvil Start
- Reroll Subscription
- Item Forge

→ Có thể là variants của entries trên hoặc được add qua patch. Engine load từ CDragon.

---

## 4. Engine impact per encounter

| Encounter | Impact tiêu biểu | Strategy adjust |
|-----------|------------------|-----------------|
| **Kayle** | Free reroll mỗi phase | Reroll comps hưởng lợi cực mạnh (Solar Kayle, Dark Ritual Elise) |
| **Ashe** | XP -2 | Fast 8/9 easier → fast-level comps hưởng lợi (Executioner Azir, Draven) |
| **Draven** | 70g cho top 2 cuối | Econ player + bleed-to-top-2 strategies |
| **Teemo** | +1 augment reroll | Picky augment users ăn value |
| **Karma** | Last augment Prismatic | Scaling augments > combat augments |
| **Kobuko** | Gold phase | Econ compounding |
| **Ornn** | Items 3-3 | Delay BIS commit → anvil |
| **Lux** | 3 emblems | Trait flex comps |
| **Yunara** | Completed anvil start | Flex opener, slam early |
| **Vi** | 2 component anvils | Hit BIS easier |

---

## 5. Engine integration

```python
@dataclass
class Encounter:
    encounter_id: str
    name: str
    description: str
    fire_phase: Literal["game_start", "stage_3_3", "last_augment", "per_phase"]
    effect_handler: str   # function name trong effect registry

# Load từ CDragon tại startup
# Encounter chọn trước game → ảnh hưởng toàn bộ decision engine

def adjust_comp_scoring_for_encounter(encounter: Encounter, comp: Comp) -> float:
    boost = 1.0
    if encounter.encounter_id == "Kayle" and comp.playstyle in ("1c_reroll", "3c_reroll"):
        boost += 0.15
    if encounter.encounter_id == "Ashe" and comp.playstyle in ("fast_8", "fast_9"):
        boost += 0.10
    if encounter.encounter_id == "Draven":
        # 70g cho top 2 → greed econ
        boost += 0.08 if comp.playstyle == "fast_9" else 0
    if encounter.encounter_id == "Karma":
        # Last augment Prismatic → scaling comps
        if comp.playstyle in ("fast_8", "fast_9"):
            boost += 0.08
    return boost
```

---

## 6. Set 18 không có Portal

Portal (Set 10 vote mechanic) **không** carry sang Set 18. Encounters thay thế hoàn toàn.
