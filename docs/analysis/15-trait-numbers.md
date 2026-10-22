# TFT — Trait Numbers (Set 18)

> Hiệu ứng chính xác mỗi breakpoint. Verify live tại startup — một số số từ LoL Wiki vs tft.tools disagree.

---

## 1. Blossom (3/5/7/9/11)

**Baseline mọi Blossom champ**: **+10% max HP** luôn luôn.

| Breakpoint | AD/AP bonus | Wisp effect |
|-----------|-------------|-------------|
| **3** | +12% | Wisps upgraded (base → + tier) |
| **5** | +30% | Wisps in **every shop** |
| **7** | +40% | **+4 gold khi mua Wisp** |
| **9** | +45% (wiki) / **+50%** (tft.tools) | **Buy 2 Wisps/round** |
| **11** | **+100%** (tft.tools) | Wisps overflow with power |

**Champions**: Karma, Yorick, Yunara, Master Yi, Ahri, Sett, Ashe.

### Blossom greed window
Breakpoint 7 fire → buy **mọi Wisp mỗi round** (ăn +4g per buy).
Breakpoint 9 → buy 2/round, double-up.
Nhiều cap-chasing boards ride tới Blossom 9 rồi pivot ra khỏi 7-Blossom (board cap cao hơn với 5-Blossom + traits khác).

---

## 2. Elderwood (3/5/7/9/11)

| Breakpoint | Effect |
|-----------|--------|
| **3** | Spawn **Stonebark Tree** + **Lifebloom** plants trên board |
| **5/7/9** | Plants lớn hơn, star-level equivalent cao hơn |
| **11** | Tất cả plants = 3★ equivalent |

### Plant mechanics
- Scale HP + AP theo Elderwood star level
- **Count as combat entity** (target-able, deal damage)
- **Không count** cho trait breakpoints của traits khác
- **Không take items**

---

## 3. Blackthorn (2/4/6)

| Breakpoint | HP gain | Bonus modifier |
|-----------|---------|----------------|
| **2** | +175 HP cho team | base |
| **4** | +300 HP | Bonus **30% stronger** |
| **6** | +550 HP | Bonus **60% stronger** |

### Mechanic
Pre-combat: **sacrifice ally trên Blackthorn hex** → team gain HP.

**Champions**: Rek'Sai, Veigar, Warwick, Azir, Malphite.

### Sacrifice decision
Engine chọn unit:
1. 1-cost từ bench (lowest value)
2. Hoặc redundant unit (không activate trait quan trọng)
3. Lowest-DPS unit trên Blackthorn hex

---

## 4. Eclipse (hidden, Solar×3 + Lunar×3)

**Effect**: Sau **8 giây combat**, kill lowest-HP enemy. Repeat **mỗi 3.5s**.

- Single-threshold trait (không stack)
- Patch 18.4 note: Riot admitted early executes "feel weak"

### Standard Eclipse comp
Kayle, Aphelios, Sejuani — reroll 3★s rồi push level cho Lunar(3), có thể Lunar Emblem.

---

## 5. Executioner

| Breakpoint | Effect |
|-----------|--------|
| **2** | +Precision (**abilities can crit**) + **+15% crit chance** |
| **3** | Enemies bleed → **+30% bonus damage over 3s** |
| **4** | Bleed scaled → **+50% bonus damage** |

### Precision keyword
Unlock crit cho abilities của holder. Interact với IE/JG overcap conversion.

---

## 6. Defender

| Breakpoint | Armor/MR bonus |
|-----------|---------------|
| **2** | +25 |
| **4** | +55–60 |
| **6** | +115–120 |

Nguồn Mobalytics + French source. Verify Set 18 live client.

---

## 7. Fae

| Breakpoint | Effect |
|-----------|--------|
| **2** | +AD/AP + heal 5% khi below 50% HP (text partial garbled) |
| **4** | Higher tiers + **extra Pixies** |

### Pixie mechanics
- Count as combat entity
- **Không take items**
- Attracted by Fae trait

---

## 8. Other traits (confirmed structure)

| Trait | Breakpoints | Mechanic |
|-------|-------------|----------|
| **Brawler** | 2/4/6 | Team max HP, Brawlers more |
| **Rapidfire** | 2/3/4/5 | AS stacking per attack |
| **Elderwood** | 3/5/7/9/11 | Plants on board |
| **Blackthorn** | 2/4/6 | Sacrifice ally |
| **Blossom** | 3/5/7/9/11 | Wisp enabler |

### Exact values chưa pull
- **Juggernaut**
- **Spellweaver**
- **Riftbeast**
- **Flora Fatalis**
- **Solar / Lunar individual** (Solar = shield + magic damage reward on 3★ boards; Lunar = AS + AP for Lunar champs + adjacent allies)

→ Engine load từ client.

---

## 9. Signature traits (single-champ)

Trait chỉ có 1 champ belong:
- **Ivern**
- **Maokai**
- **Zyra**

Treat như solo-trait buff, không activate breakpoint logic.

---

## 10. Engine data structure

```python
@dataclass
class TraitData:
    trait_id: str
    name: str
    breakpoints: list[int]
    effects: dict[int, TraitEffect]
    champions: list[str]

    # Mechanics
    enables_hidden_trait: str | None = None   # Solar+Lunar → Eclipse
    requires_pair: tuple[str, str] | None = None

@dataclass
class TraitEffect:
    breakpoint: int
    stat_bonuses: dict[str, float]      # {"max_hp_pct": 0.10, ...}
    ability_description: str
    special_handler: str | None = None  # function trong trait registry
```

---

## 11. Hằng số

```python
# Blossom
BLOSSOM_BASE_HP_PCT = 0.10
BLOSSOM_BONUS_PCT = {
    3: 0.12,
    5: 0.30,
    7: 0.40,
    9: 0.45,     # or 0.50 per tft.tools
    11: 1.00,
}
BLOSSOM_WISP_GOLD_BONUS = 4   # at breakpoint 7
BLOSSOM_WISPS_PER_ROUND = {3: 1, 5: 1, 7: 1, 9: 2, 11: 2}

# Blackthorn
BLACKTHORN_HP = {2: 175, 4: 300, 6: 550}
BLACKTHORN_BONUS_MULT = {2: 1.00, 4: 1.30, 6: 1.60}

# Executioner
EXECUTIONER_CRIT_BONUS = {2: 0.15}
EXECUTIONER_BLEED_PCT = {3: 0.30, 4: 0.50}
EXECUTIONER_BLEED_DURATION_SEC = 3.0

# Eclipse
ECLIPSE_FIRST_EXECUTE_SEC = 8.0
ECLIPSE_REPEAT_SEC = 3.5

# Defender
DEFENDER_RES_BONUS = {2: 25, 4: 57, 6: 117}
```
