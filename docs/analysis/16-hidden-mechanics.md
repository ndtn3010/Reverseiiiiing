# TFT — Hidden & Advanced Mechanics

> Targeting, pathfinding, mana lock, dodge, event order. Những cơ chế không hiện trên tooltip.

---

## 1. Targeting / Aggro

### Default rule
Mỗi unit target **closest enemy by hex distance** tại combat start.

- **Ties**: random selection
- **No valid path**: unit retarget
- **Target chết**: retarget closest

### Exceptions

| Champ / Effect | Behavior |
|---------------|---------|
| **Caitlyn** | Target furthest unit, nhưng hit first unit along shot path |
| **Azir / Ezreal** | Soldiers/proxies có aggro riêng, redirect to closest tank (split-aggro rule for summoned units) |
| **Zephyr** | Banish mirrored enemy 5s (mirror qua hex (1.5, 3)) |
| **Shroud of Stillness** | Delay casts of enemies trong 3-wide line từ Shroud hex |
| **Taunt** | Force adjacent enemies target the taunter |

### Zephyr + untargetable interaction
- Zephyr banish **override** taunt (banished unit gone from fight)
- Zephyr banish **already-dead unit** → no refund, charge wasted

### Shroud vs 0-mana units
- Delay cast ~5s → unit cast first bị trễ hẳn

---

## 2. Pathfinding

- Hex adjacency = **6 neighbors** cho interior cells
- Edges = 4 neighbors
- Corners = 2 neighbors
- Units **reposition liên tục** mid-combat nếu target unreachable hoặc dies
- **Không có fixed turn order** — real-time simulation

---

## 3. Mana lock

| Scenario | Lock duration |
|----------|---------------|
| Default | **1.0 giây** sau cast ends |
| Draven axe cycle | Full cycle (longer than 1s) |
| Channeled abilities | Per-unit, longer |

**Mana generate trong lock = LOST**. Engine phải simulate lock window per cast.

---

## 4. Damage event order

- **t=0.0**: units lock current target, start moving/attacking
- **Không deterministic "who hits first"** — simulated per attack-speed timer
- Simultaneous casts resolve per cast order queue (client-side server-authoritative)
- Engine treat là **effectively simultaneous**, use expected-value math

---

## 5. Dodge chance

- **Sparring Gloves** old sets: +5% dodge
- **Current Set 18 role**: primarily crit component
- Dodge có thể còn exist trong Set 18 nhưng không confirmed trong search
- Treat là **deprecated** unless engine find live dodge stat
- Historical cap: 100%

---

## 6. Stealth / Untargetable

| Source | Duration |
|--------|----------|
| **Edge of Night** | 1s untargetable khi drop <50% HP |
| **Zhonya's Hourglass equivalent** (nếu có Set 18) | 2s untargetable |
| **Fiora/Akshan dodge/evade** | Per-ability |

### Untargetable rules
- **Không bị hit** bởi targeted ability hoặc basic attack
- **TAKE AoE damage** vẫn
- Engine flag: `is_untargetable: bool` per unit, check trước mọi target-selection

---

## 7. Spawn / Summon mechanics

### Elderwood plants + Fae pixies
- **Count as combat entity** (target-able, deal damage)
- **Không count** cho trait breakpoints của traits khác
- **Không take items**
- Engine: treat as `SummonedUnit` subclass

### Azir soldiers
- Temporary projectiles tied to ability
- **Không phải independent unit**
- Không take items, không count traits

---

## 8. Overcapping

| Stat | Behavior |
|------|---------|
| **AS** | Clamp **5.0** attacks/sec |
| **Mana** | Discard above max (overcap lost) |
| **Crit chance** | Convert to crit damage per Precision rules (+10% CD per 25% overcap) |
| **AP / AD** | **No cap**, pure additive |

---

## 9. Round structure timing

| Phase | Duration | Notes |
|-------|----------|-------|
| Planning phase (standard) | **~30s** | Not confirmed Set 18, long-standing convention |
| Planning phase (Stage 1) | ~30s initial, auto-advance when all ready | |
| Combat phase | **Auto-draw ~30s** | Nếu neither board eliminated |
| Carousel countdown | ~30s cycle | HP-order release in pairs mỗi ~5s |
| Augment armory | Visible trong planning phase của 2-1/3-2/4-2 | 1 reroll (replace all 3) |

### Patch 18.4 pacing cut
- **Combat arrival + departure phases −1s each**
- Tiết kiệm ~1 phút per game

→ Engine treat planning + combat là **~30s** mỗi cái cho tới khi confirm từ live client.

---

## 10. Combat edge cases

### Zephyr + taunt
Zephyr banish wins — banished unit gone from fight entirely.

### Shroud vs low-cost caster
0-mana units bị delay cast ~5s → effectively first-cast locked out.

### Simultaneous unit death
Nếu 2 units deal lethal cùng frame → engine resolve theo cast order queue, kết quả per server authoritative.

### Augment-item edge cases
- **Pandora's Items**: swap items mỗi PvP round → có thể grief narrow-BIS carry
- **Thief's Gloves + Hero augment**: certain hero augment lock Thief's roll result → engine flag `all_slots_fixed`
- **Ornn's Forge**: 3 artifact offered, pick 1 → artifact count 2 hoặc 3 slot

### Carousel item pickup
- **Pre-attach**: không drop component lên carousel champ mid-grab
- **Grabbed champ inherits**: held item(s) + component dùng để grab
- **Carousel champs**: count là **1-cost cho pool purposes** (freshly minted, not drawn from pool)

---

## 11. Engine simulation stub

```python
class CombatSimulator:
    def __init__(self, my_board: list[Unit], enemy_board: list[Unit]):
        self.my_units = my_board
        self.enemy_units = enemy_board
        self.time = 0.0
        self.events: list[CombatEvent] = []

    def tick(self, dt: float = 0.05):
        """Simulate 1 tick (50ms resolution)."""
        self.time += dt

        for unit in self.alive_units:
            # Target acquisition
            if unit.target is None or not unit.target.alive:
                unit.target = self.find_target(unit)

            # Movement
            if not unit.in_attack_range(unit.target):
                self.move_toward(unit, unit.target)
                continue

            # Attack
            if unit.ready_to_attack(self.time):
                dmg = self.compute_attack_damage(unit, unit.target)
                self.apply_damage(unit.target, dmg)
                unit.last_attack = self.time
                unit.mana = min(unit.mana + MANA_PER_ATTACK, unit.max_mana)

            # Cast ability
            if unit.mana >= unit.max_mana and not unit.mana_locked(self.time):
                self.cast_ability(unit)
                unit.mana = 0
                unit.mana_lock_until = self.time + unit.mana_lock_sec

    def find_target(self, unit):
        """Default: closest enemy by hex distance."""
        enemies = [e for e in self.enemy_units if e.alive and not e.is_untargetable]
        if not enemies:
            return None
        return min(enemies, key=lambda e: hex_distance(unit.pos, e.pos))
```

---

## 12. Hằng số

```python
PLANNING_PHASE_SEC = 30
COMBAT_TIMEOUT_SEC = 30
CAROUSEL_HP_PAIR_RELEASE_SEC = 5

# Combat tick resolution
SIM_TICK_SEC = 0.05   # 20 FPS equivalent

# Default behaviors
DEFAULT_MANA_LOCK_SEC = 1.0
DEFAULT_TARGETING = "closest_by_hex"

# Summoned units
SUMMON_COUNTS_FOR_TRAITS = False
SUMMON_TAKES_ITEMS = False
```
