# TFT — Item Stats (Số liệu chính xác)

> 36 completed items + top radiants. Patch 18.2–18.4b values. Verify live tại startup.

---

## 1. Carry items — stats đầy đủ

### Attack damage carries

| Item | Recipe | Stats | Effect |
|------|--------|-------|--------|
| **Infinity Edge** | BF + Gloves | +35% AD, +35% crit chance | Convert crit damage portion → **true damage**. Mỗi extra Precision stack: +10% crit damage |
| **Jeweled Gauntlet** | Rod + Gloves | +35 AP, +35% crit chance | **Abilities crit**. Precision overcap conversion giống IE |
| **Guinsoo's Rageblade** | Bow + Rod | +10% AS, +10 AP | Stack **+7% AS/second**, unlimited. Radiant: +20 AP, +25% AS, +16%/stack |
| **Spear of Shojin** | BF + Tear | +15 AD, +15 mana per attack | On attack: +5 mana extra |
| **Giant Slayer** | BF + Bow | +15 AD, +15% AS | +25% bonus damage vs ≥1800 HP targets |
| **Last Whisper** | Bow + Gloves | +15% AS, +15% crit | On attack: Sunder target 30% armor cho 3s |
| **Red Buff** | Bow + Belt | +10% AS, +150 HP | Burn 1%/sec max HP + apply Grievous Wounds |

### AP carries

| Item | Recipe | Stats | Effect |
|------|--------|-------|--------|
| **Rabadon's Deathcap** | Rod + Rod | +75 AP | Flat AP spike. Radiant: higher AP + damage amp |
| **Blue Buff** | Tear + Tear | +25 start mana, +25 max mana | Sau cast: next cast rẻ hơn + bonus damage |
| **Archangel's Staff** | Tear + Rod | +15 AP, +15 mana | Gain **+25 AP mỗi 5s** indefinitely |
| **Hextech Gunblade** | Rod + Tear | +15 AP, +15 mana | Heal 25% damage dealt. Overheal → shield lowest-HP ally |
| **Morellonomicon** | Rod + Belt | +30 AP, +150 HP | Burn + Grievous Wounds |

---

## 2. Tank items

| Item | Recipe | Stats | Effect |
|------|--------|-------|--------|
| **Warmog's Armor** | Belt + Belt | +12% max HP | Flat HP amp |
| **Gargoyle Stoneplate** | Vest + Gloves | +18 armor, +18 MR | +18 armor và MR cho mỗi enemy đang target holder |
| **Bramble Vest** | Vest + Vest | +60 armor | 75% physical reduction trên crits. On hit: AoE magic |
| **Dragon's Claw** | Negatron + Negatron | +60 MR | Reduce incoming magic 60%. Heal từ magic damage taken |
| **Protector's Vow** | Vest + Tear | +25 armor, +25 MR | Shield proc below 50% HP |
| **Edge of Night** | BF + Vest | +15 AD, +25 armor | <50% HP: untargetable 1s + 15% AS + tenacity |
| **Titan's Resolve** | Bow + Vest | +15% AS, +25 armor | Stack AD/AP on hit/take hit. Full stack: +25 armor/MR |
| **Sunfire Cape** | Belt + Vest | +150 HP, +20 armor | AoE magic burn hex-adjacent enemies |

---

## 3. Top radiants (Patch 18.4)

| Radiant | Rank | Note |
|---------|------|------|
| **Radiant Blue Buff** | S+ | Carry mana engine |
| **Radiant Rabadon's Deathcap** | S+ | AP spike |
| Radiant Morellonomicon | S | 25.47% WR |
| Radiant Evenshroud | S | AoE sunder support |
| Radiant Thief's Gloves | S | Metabot 10/11 |
| Radiant Infinity Edge | A | +75% AD, +75% crit |
| Radiant Jeweled Gauntlet | A | +75 AP, +75% crit |
| Radiant Guinsoo's Rageblade | A | +20 AP, +25% AS, +16%/stack |
| Radiant Hand of Justice | A | — |

Nguồn radiant:
- Augment (Pandora's Items, Radiant Relics)
- Ornn's Forge
- Specific Wisps (Set 18)

---

## 4. Item uniqueness rules

### Unique items
- Items có **"Unique"** tooltip không được equip 2 lần trên **cùng** champ
- Confirmed stable từ patch 9.18
- **Spatula-emblems**: luôn Unique
- Hầu hết carry items hiện tại ARE unique → engine assume unique unless marked otherwise

### Legal stacking
- **IE + JG** trên cùng unit: cả 2 unique riêng, crit chance stack **additively** → legal
- **2 emblems khác nhau** trên cùng champ: legal (mỗi emblem = trait khác nhau)

### Illegal
- Same emblem 2 lần: illegal (1 slot/emblem type)
- Same unique item 2 lần: illegal

### Ornn artifacts
- Unique
- **3-slot items** (chiếm cả 3 slot)
- Không stack với chính nó
- Example: Blacksmith's Gloves

### Radiant + base
- Mutually exclusive (treat 1 slot = 1 item type)
- Engine không confirm stackable → mặc định no

---

## 5. Hidden item effect interactions

### Mortal Reminder / Grievous Wounds
- Apply **-50% healing** debuff
- Stack với Red Buff burn
- Giant Slayer condition ≥1800 HP triggered trước mitigation

### Edge of Night proc
- Chỉ fire 1 lần/combat
- Reset mỗi fight
- Untargetable 1s + stat buff

### Guinsoo's stack cap
- Theory: unlimited
- Reality: AS clamp 5.0 → stack past cap = wasted raw AS
- Nhưng **separate on-attack damage** từ Rageblade **không clamp**

### Thief's Gloves
- Lock cả 3 slot (không add item khác)
- Re-roll items mỗi stage với level-based tier
- Hero augment interactions: certain hero augment lock Thief's roll result
- Engine flag: `thiefs_gloves = {all_slots_fixed: True, no_flex: True}`

---

## 6. Engine data structure

```python
@dataclass
class ItemData:
    item_id: str
    name: str
    recipe: tuple[str, str] | None   # 2 components, None cho component itself

    # Stats
    bonus_ad_pct: float = 0.0
    bonus_ap: int = 0
    bonus_as_pct: float = 0.0
    bonus_hp_pct: float = 0.0
    bonus_hp: int = 0
    bonus_armor: int = 0
    bonus_mr: int = 0
    bonus_crit_chance: float = 0.0
    bonus_crit_damage: float = 0.0
    bonus_mana: int = 0
    bonus_start_mana: int = 0

    # Flags
    unique: bool = True
    is_emblem: bool = False
    is_radiant: bool = False
    is_ornn_artifact: bool = False
    slot_count: int = 1

    # On-hit / passive effects (dynamic callbacks)
    effect_description: str = ""
    effect_handler: str | None = None   # function name trong effect registry
```

---

## 7. Hằng số BIS lookup

```python
BIS_BY_CARRY = {
    "Azir": [
        ["Spear of Shojin", "Guinsoo's Rageblade", "Jeweled Gauntlet"],
        ["Spear of Shojin", "Giant Slayer", "Jeweled Gauntlet"],   # Executioner shell
    ],
    "Kayle": [
        ["Guinsoo's Rageblade", "Jeweled Gauntlet", "Hextech Gunblade"],
    ],
    "Rengar": [
        ["Infinity Edge", "Jeweled Gauntlet", "Bloodthirster"],
        ["Guinsoo's Rageblade", "Titan's Resolve", "Edge of Night"],   # Defender
    ],
    "Draven": [
        ["Infinity Edge", "Last Whisper", "Bloodthirster"],
    ],
    "KhaZix": [
        ["Infinity Edge", "Hand of Justice", "Bloodthirster"],
    ],
    "ElderDragon": [
        ["Spear of Shojin", "Jeweled Gauntlet", "Warmog's Armor"],
    ],
    "Elise": [
        ["Radiant Gargoyle Stoneplate", "Hextech Gunblade", "Jeweled Gauntlet"],
    ],
    "Nidalee": [
        ["Rabadon's Deathcap", "Jeweled Gauntlet", "Spear of Shojin"],
    ],
    "Veigar": [
        ["Spear of Shojin", "Blue Buff", "Void Staff"],
        ["Spear of Shojin", "Blue Buff", "Jeweled Gauntlet"],
    ],
}
```
