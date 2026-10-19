# TFT — Combat Math (Deep Dive)

> Công thức sát thương chính xác cho engine simulator. Set 18 · Patch 18.4.

---

## 1. Damage pipeline đầy đủ

```
raw_damage        = ability_damage HOẶC attack_damage
mitigated_damage  = raw_damage × (100 / (100 + resistance))
                    # resistance = armor (physical) hoặc MR (magic)
after_shred       = raw_damage × (100 / (100 + resistance × (1 - shred_pct)))
after_dr          = after_mitigated × (1 - damage_reduction_pct)
                    # DR nhân sau mitigation, multiplicative
true_damage       = raw_damage
                    # bypass tất cả mitigation + DR
```

### Verify armor/MR
Công thức League-style **100/(100+R)**:

| Armor | % reduction |
|-------|-------------|
| 15 | ~13% |
| 45 | ~31% |
| 100 | 50% |
| 200 | 66.7% |
| 300 | 75% |

### Sunder / Shred
- Cả 2 đều **giảm 30% resistance** của target
- Sunder = armor shred (physical)
- Shred = MR shred (magic)

### Damage reduction (DR)
- Multiplicative, apply **sau** mitigation
- Ví dụ: 50% DR + 50% mitigation trên 100 damage = `100 × 0.5 × 0.5 = 25`

---

## 2. Basic attack damage

```
hit_damage = AD × (1 + crit_damage_bonus)   nếu crit
             AD                              nếu không
```

- **Base crit damage**: **140%** (crit 100 AD = 140 damage trước mitigation)
- **Crit chance cap**: **100%** từ rolling layer
- **Overcap crit** → convert thành **+10% crit damage per 25% overcap** (Infinity Edge Precision)

---

## 3. Ability damage

```
spell_damage = base_spell_damage × (1 + (AP - 100) / 100)
```

- Baseline AP = **100** (= 100%)
- Mọi AP bonus apply như `(1 + bonus_pct)` multiplier
- Abilities **không crit mặc định**
- Jeweled Gauntlet + Executioner Precision mở unlock crit cho abilities

---

## 4. Mana generation

| Mechanic | Value |
|----------|-------|
| Mana/basic attack | **10** (kể cả bị dodge/parry) |
| Mana/damage taken | **1 mana per 1% max HP** (post-mitigation), **cap 42.5/hit** |
| Starting mana | per-unit |
| **Mana lock sau cast** | **1.0s** default; Draven = full axe cycle |
| Max mana | per-unit cap, overcap discard |

### Mana items
- **Spear of Shojin**: +5 mana per attack (total 15)
- **Blue Buff**: +20 mana sau mỗi cast, giảm max mana cast kế
- **Adaptive Helm**: +15 mana/3s (frontline) hoặc +1/attack (backline)

> Lưu ý: Set 15 có role-based mana (tank 5, caster 7+2/sec). Set 18 không confirm — treat là classic 10 baseline cho tới khi unit sheet nói khác.

---

## 5. Attack speed

```
AS_effective = base_AS × (1 + bonus_AS_pct)
```

- **AS cap**: **5.00 attacks/sec**, enforced từ Set 7/8
- Patch 18.4 không raise cap → engine phải **clamp 5.0**
- **Overcap behavior**: Rageblade push qua cap bằng separate on-attack damage, AS display vẫn clamp

---

## 6. Crit stacking

```python
crit_chance_display = min(1.00, sum(all_crit_sources))

if crit_chance_display > 1.00:
    excess = crit_chance_display - 1.00
    # +10% crit damage per 25% overcap (IE Precision)

crit_damage_mult = 1.40 + bonus_crit_damage
```

- **IE + JG** trên cùng unit: cả 2 unique riêng, nhưng crit chance **cộng additively** → legal
- IE "true damage crit" là **type conversion**, không phải multiplier phụ

---

## 7. Lifesteal / Omnivamp

| Type | Nguồn heal |
|------|-----------|
| **Lifesteal** | % damage từ basic attack only |
| **Omnivamp** | % damage từ **mọi nguồn** (attack + ability) |

- **Bloodthirster**: overheal → shield cap **25% max HP**
- **Hand of Justice**, **Hextech Gunblade**: omnivamp
- **Grievous Wounds** / **Mortal Reminder**: giảm healing **50%**

---

## 8. Shield mechanics

- Shield absorb **trước HP**, order FIFO (Set 18 chưa confirm, treat oldest-first safe)
- **Shield damage KHÔNG generate mana** cho unit được shield

| Shield type | Behavior |
|-------------|----------|
| **Self-shield** (Protector's Vow proc) | Refreshable |
| **Applied shield** (Locket aura) | Không stack cùng source |
| **Overheal shield** (Bloodthirster) | Cap 25% max HP |

---

## 9. CC durations & tenacity

```
cc_duration_actual = cc_base × (1 - tenacity_pct)
```

- Tenacity sources stack **multiplicatively**
- **Edge of Night**: drop <50% HP → 100% tenacity + 15% AS + untargetable brief
- **Immune** = full ignore (không có reduction formula)

---

## 10. Engine hardcode

```python
# Combat math
ARMOR_MITIGATION = lambda r: 100 / (100 + r)
MR_MITIGATION = lambda r: 100 / (100 + r)
SUNDER_PCT = 0.30
SHRED_PCT = 0.30

BASE_CRIT_DAMAGE = 1.40
CRIT_CAP = 1.00
BASELINE_AP = 100
AS_CAP = 5.00

# Mana
MANA_PER_ATTACK = 10
MANA_PER_DAMAGE_TAKEN_CAP = 42.5
MANA_LOCK_DEFAULT_SEC = 1.0

# Healing
GRIEVOUS_WOUNDS_PCT = 0.50
BLOODTHIRSTER_SHIELD_CAP_PCT = 0.25
```

---

## 11. End-of-round damage (HP mất khi thua)

### Công thức
```
hp_damage = stage_base_damage + alive_enemy_unit_count
```

Mỗi unit sống của đối thủ = **+1 HP damage**, bất kể star level hay cost.
PvE round, carousel, augment armory **không gây HP damage**.

### Stage base damage (Set 18 — 2 nguồn disagree)

| Stage | TFT Ninja / OP.GG | TFTips / TFT Flow |
|-------|------------------|-------------------|
| 1 | 0 | 0 |
| 2 | 2 | 2 |
| 3 | 5 | 6 |
| 4 | 8 | 7 |
| 5 | 10 | 10 |
| 6 | 12 | 12 |
| 7+ | 17 | 17 |
| 8+ | — | 150 (sudden-death?) |

→ Engine default **TFT Ninja/OP.GG column**, Stage 8+ 150 là sudden-death escalation.

```python
STAGE_BASE_DAMAGE = {1: 0, 2: 2, 3: 5, 4: 8, 5: 10, 6: 12, 7: 17}
# + 1 per alive enemy unit
```

### Augment interactions
- **Last Stand**: buff below 40 HP, không đổi formula
- **Golden Gamble**: raise interest cap, không touch damage
- Không augment nào Set 18 confirmed đổi end-of-round damage formula

---

## 12. Damage simulation stub

```python
def simulate_damage(
    attacker: Unit,
    defender: Unit,
    damage_type: Literal["physical", "magic", "true"],
    base_damage: float,
    is_crit: bool = False,
) -> float:
    raw = base_damage

    if is_crit:
        raw *= attacker.crit_damage_mult   # default 1.40 + bonuses

    if damage_type == "true":
        return raw * (1 - defender.damage_reduction)

    resistance = defender.armor if damage_type == "physical" else defender.mr
    if damage_type == "physical" and attacker.has_sunder(defender):
        resistance *= (1 - SUNDER_PCT)
    if damage_type == "magic" and attacker.has_shred(defender):
        resistance *= (1 - SHRED_PCT)

    mitigated = raw * (100 / (100 + resistance))
    final = mitigated * (1 - defender.damage_reduction)

    return final
```
