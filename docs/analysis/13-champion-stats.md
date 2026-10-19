# TFT — Champion Stats (Top Meta Carries)

> Stat gốc + ability + BIS cho 9 top carry Set 18. Nguồn: Metabot, SeeMeta, OP.GG (patch 18.3/18.4). Verify live tại startup.

---

## 1. Azir — 5-cost, Executioner / Flora Fatalis

| Stat | 1★ | 2★ | 3★ |
|------|----|----|----|
| HP | 650 | 1170 | 2106 |
| AD | 30 | 45 | 68 |
| Armor | 35 | 35 | 35 |
| MR | 35 | 35 | 35 |
| AS | 0.75 | 0.75 | 0.75 |
| Range | 4 | 4 | 4 |
| Crit chance | 25% | 25% | 25% |
| Start/Max mana | 0 / 35 | | |

### Ability — Arise! (35 mana)
+150% AS for 6 attacks. Next 6 attacks replaced với soldier-command magic hits dealing **43/65/103** magic damage (patch 18.3).

- 18.1/18.2 version: 46/69/110
- OP.GG lists: 40/60/96
→ Engine load từ live patch data

### BIS
Spear of Shojin (mana loop → more Arise! casts) + Rageblade (soldier commands stack AS) + Jeweled Gauntlet (soldier commands crit).
**Executioner shell**: swap Rageblade → Giant Slayer.

---

## 2. Kayle — 4-cost, Solar + Rapidfire

| Stat | 1★ | 2★ | 3★ |
|------|----|----|----|
| HP | 550 | 990 | 1782 |
| Armor | 30 | 30 | 30 |
| MR | 30 | 30 | 30 |

### Ability — Solar Judgment
On-hit bonus magic damage **56/84/98** (OP.GG EN) hoặc **62/92/105** (OP.GG DK, patch khác).
Secondary wave: 35 hoặc 40 tùy version.

### BIS
Rageblade + Jeweled Gauntlet + Hextech Gunblade (sustain + AS stacking).
Gargoyle Stoneplate cho Ornn frontline.

---

## 3. Rengar — 4-cost

| Stat | 1★ | 2★ | 3★ |
|------|----|----|----|
| HP | 900 | 1620 | 2916 |
| AD | 60 | 90 | 135 |

### Ability — Savagery (10/50 mana)
Leap to lowest-HP enemy trong 3 hex, deal **255/385/615** physical damage, heal up to **150/220/220** scaling với missing HP (AP ratio).

### BIS
- **Standard**: Infinity Edge + Jeweled Gauntlet + Bloodthirster
- **Defender shell** (TFT Academy): Rageblade + Titan's Resolve + Edge of Night

---

## 4. Draven — 5-cost, Elderwood

| Stat | 1★ | 2★ | 3★ |
|------|----|----|----|
| HP | 900 | 1620 | 2916 |
| AD | 48 | 72 | 108 |
| Start/Max mana | 0 / 110 (18.3; was 120 trong 18.1) | | |

### Ability — Whirling Death
Throw 2 axes at most-bleeding enemy, deal **100/150/400** physical, consume bleeds.
Returning axes: +**30/45/100** physical.

### BIS
Infinity Edge + Last Whisper + Bloodthirster (hoặc Jeweled Gauntlet swap cho crit).

---

## 5. Kha'Zix — 3-cost

| Stat | 1★ | 2★ | 3★ |
|------|----|----|----|
| HP | 950 | 1710 | 3078 |
| AD | 40 | 60 | 90 |
| Armor | 55 | 55 | 55 |
| MR | 55 | 55 | 55 |
| AS | 0.85 | | |
| Range | 1 | | |
| Start/Max mana | 0 / 25 | | |

### Ability — Taste Their Fear
Leap 3 hex, deal **285/400/580** magic.
Nếu target không có adjacent ally: **310/445/660** + 10 mana refund.
18.1/18.2 version: 2.7 hex range, 260/370/550.

### BIS
Infinity Edge + Hand of Justice + Bloodthirster.

---

## 6. Elder Dragon — 5-cost, Apex Predator + Riftbeast

| Stat | 1★ | 2★ | 3★ |
|------|----|----|----|
| HP | 1800 | 3240 (×1.8) | 5832 |
| AD | 125 | 225 | 405 |
| Armor | 75 | | |
| MR | 75 | | |
| AS | 0.50 | | |
| Range | 2 | | |
| Crit chance | 25% | | |
| Start/Max mana | 20 / 60 | | |

### Ability — Heat Without Equal
Replace ability với Flame Breath on cast:
1. Become invulnerable
2. Fly up
3. Land dealing AoE
4. Stun enemies
5. Grant Omnivamp
6. Apply ignite DoT

Exact scaling không public — SeeMeta inferred từ client.

### BIS
Hybrid AP + tank: Spear of Shojin + Jeweled Gauntlet + Warmog's.

---

## 7. Elise — 2-cost, Coven + Vanguard

### Ability
Spider form transformation, magic damage + healing scale với AP, decaying AS sau mỗi cast tiếp.

- 18.4 raw tier: below average (33.4% top-4 Metabot sample)
- **Dark Ritual augment** biến Elise thành carry

### BIS (Dark Ritual Reroll)
Radiant Gargoyle Stoneplate + AP items.

---

## 8. Nidalee — 4-cost, Lunar

| Stat | 1★ |
|------|----|
| HP | 850 |
| AD | 35 |

### Ability — Javelin
**170/255/2000** damage. Every 3rd hit: **320/480/3000**.
(Số 3★ có vẻ là client-side display inflation — treat là "massive".)

### BIS
AP carry build: Rabadon + Jeweled Gauntlet + Spear of Shojin.

---

## 9. Veigar — A-tier reroll carry

### Ability
Burst AP magic damage.

### BIS
Spear of Shojin + Blue Buff + Void Staff HOẶC Jeweled Gauntlet.

---

## 10. Engine data structure

```python
@dataclass
class ChampionData:
    champ_id: str
    cost: int
    traits: list[str]

    # Base stats (1★)
    hp: int
    ad: int
    armor: int
    mr: int
    attack_speed: float
    range: int
    crit_chance: float = 0.25
    crit_damage: float = 1.40

    # Mana
    start_mana: int
    max_mana: int

    # Ability
    ability_name: str
    ability_mana_cost: int
    ability_damage_per_star: list[int]   # [1★, 2★, 3★]
    ability_damage_type: Literal["physical", "magic", "true"]
    ability_ap_ratio: float
    ability_description: str
    special_mana_lock_sec: float | None = None

    def scale_to_star(self, star: int) -> ChampionData:
        mult = {1: 1.0, 2: 1.8, 3: 3.24}[star]
        return replace(self,
            hp=int(self.hp * mult),
            ad=int(self.ad * mult),
            ability_damage=self.ability_damage_per_star[star - 1],
        )
```

### Star scaling rule
```
HP:  1★ × 1.8^(star-1)   (2★ = 1.8×, 3★ = 3.24×)
AD:  same multiplier
Armor/MR: không scale (giữ nguyên)
AS: không scale
```

Verify từng champ ở live client — một số champ có exception (Elder Dragon HP ratio 1.8x confirmed, AD 1.8x confirmed).
