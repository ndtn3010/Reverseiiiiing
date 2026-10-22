# TFT — Carousel & Item Theory (Deep Dive)

> Carousel strategy, component priority, slam decisions, radiant/artifact.

---

## 1. Carousel pick order

- **Carousel đầu tiên (1-4)**: cả 8 người thả cùng lúc, không có HP priority. Vị trí mặt đất quan trọng, không phải HP.
- **Carousel sau (X-4, X ≥ 2)**: thả theo cặp theo HP, **HP thấp nhất pick trước**. HP cao nhất pick cuối.

→ **Being low-HP trên carousel round là tốt.** Bot lobby lấy đồ xịn. 25 HP đánh bại 90 HP tới chỗ Spatula routine.

---

## 2. Component priority ranking (Set 18 patch 18.4)

| Tier | Components | Lý do |
|------|------------|-------|
| **S** | B.F. Sword, Needlessly Large Rod, Giant's Belt | Items hoàn chỉnh chất lượng nhất patch này |
| **A** | Tear of the Goddess | Blue Buff / Shojin / Archangel đều dùng được nhiều carry |
| **B** | Chain Vest, Negatron Cloak | Defensive flex, cần cho Gargoyle Stoneplate |
| **C** | Recurve Bow | Chỉ mạnh cho AS carries (Kayle, Rapidfire) |
| **C** | Sparring Gloves | Crit-dependent carries only; cũng tạo Thief's Gloves |
| **Variable** | Spatula | S nếu comp cần emblem, nếu không C |

### Flex score mỗi component

| Component | Flex | Items hoàn chỉnh phổ biến |
|-----------|------|---------------------------|
| **B.F. Sword** | 10/10 | IE, Shojin, Deathblade, BT, HoJ, Giant Slayer |
| **Rod** | 10/10 | Rabadon, Morello, JG, Hextech, Nashor |
| **Tear** | 9/10 | Shojin, Blue Buff, Archangel's, Hextech, Chalice |
| **Belt** | 7/10 | Warmog, Dragon's Claw, Sunfire — mostly frontline |
| **Vest** | 6/10 | Bramble, Gargoyle, Sunfire, Edge of Night |
| **Negatron** | 5/10 | Dragon's Claw, QSS, Edge of Night |
| **Bow** | 5/10 | Rageblade, Red Buff, Nashor — AS only |
| **Gloves** | 4/10 | Shiv, HoJ, Thief's — niche |
| **Spatula** | depends | S nếu emblem mở trait, else holds items |

---

## 3. Carousel scoring formula

```
score(pick) = w_component_need[c] × 2.0       # comp đang cần component này mức nào
            + w_item_flexibility[c] × 1.0     # phục vụ được bao nhiêu carry
            + w_champ_value[champ] × 0.8      # 2★ carry > component
            + w_spatula_bonus × 1.5           # nếu emblem mở trait
            - w_wasted_component × 0.5        # component thứ 4 cùng loại là dead
```

**Loss-streak special**: ưu tiên **Rod** (làm Morellonomicon / Rabadon cho AP carry, ceiling cao).

---

## 4. Slam decision rules

### Threshold theo HP

| HP | Slam rule |
|----|-----------|
| ≥70 | Hold nếu đợi BIS cụ thể + đã có holder trên bench |
| 50–70 | Slam flex items (Rageblade, Shojin, Warmog, Bramble) |
| 30–50 | Slam bất cứ gì playable, kể cả item narrow |
| <30 | Slam mọi component vào bất kỳ item nào, bất kỳ order |

### Items luôn slammable (flex)
- **Guinsoo's Rageblade** (any AS carry)
- **Warmog's** (any frontline)
- **Bramble Vest** (counter AD)
- **Spear of Shojin** (any ability carry)
- **Gargoyle Stoneplate** (any tank)
- **Protector's Vow** (any frontline)

### Items đáng hold
- 3-item sets (Thief's Gloves + hero augment cụ thể)
- Jeweled Gauntlet trên crit carry cụ thể

---

## 5. Slam cost model

```
HP_cost_of_holding = (rounds_waiting × avg_damage_delta_without_item)
                   + probability_not_hitting_target × full_item_value_lost
```

**Rule of thumb**: nếu `HP_cost_of_holding > 10 HP` → slam ngay.

---

## 6. Radiant items (patch 18.4)

Top SeeMeta radiant tier:

| Rank | Radiant |
|------|---------|
| S+ | **Radiant Blue Buff** |
| S+ | **Radiant Rabadon's Deathcap** |
| S | Radiant Morellonomicon (25.47% WR, low pick) |
| S | Radiant Evenshroud |
| S | Radiant Thief's Gloves (per Metabot 10/11) |
| A | Radiant Guinsoo's / Radiant Hand of Justice |

Nguồn radiant: augment (Pandora's Items, Radiant Relics), Ornn's Forge, specific Wisps.

---

## 7. Artifact / Ornn items

- **Ornn's Forge** = augment cho radiant/Ornn artifact. S-tier khi fit (Lich Bane trên Solar Akali).
- Artifact tier list cụ thể per-patch không surfaced trong search. Engine phải treat artifact rating như lookup per-comp, không rank global.

---

## 8. Slam priority (patch 18.4)

**Carry items**:
- Guinsoo's Rageblade (Kayle, Azir, Rengar)
- Jeweled Gauntlet
- Infinity Edge
- Spear of Shojin

**Tank items**:
- Warmog's
- Gargoyle Stoneplate
- Bramble Vest
- Dragon's Claw

**Universal flex slams**:
- Rageblade, Warmog, Shojin, Bramble, Gargoyle

---

## 9. Component tracking (engine)

```python
@dataclass
class ComponentState:
    inventory: list[Component]
    on_units: dict[str, list[Item]]
    needed_bis: dict[str, list[Component]]   # champ → components còn thiếu

    def should_slam(self, state: GameState, meta: MetaDB) -> SlamDecision | None:
        if state.hp < 30:
            return SlamDecision(aggressive=True, item=self.best_slam_any())
        if state.hp < 50 and self.has_flex_components():
            return SlamDecision(item=self.flex_slam())
        if self.hp_cost_of_holding(state) > 10:
            return SlamDecision(item=self.flex_slam())
        return None
```
