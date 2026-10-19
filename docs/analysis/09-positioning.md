# TFT — Positioning & Scouting (Deep Dive)

> Positioning là quyết định cuối cùng mỗi round. Memory read cho phép engine scout mọi opponent trong <1ms.

---

## 1. Hex grid

Grid 4 hàng × 7 cột = 28 ô (số usable slots scale với level).
- Hàng 0 = sát ta (frontline)
- Hàng 3 = xa nhất (backline)
- Mỗi ô có 2–6 láng giềng (góc = 2, cạnh = 4, giữa = 6)

### Key positions
- **Corner (0,0), (0,6), (3,0), (3,6)**: 2 láng giềng — assassin/diver bait hoặc chỗ carry an toàn nhất
- **Second row from back** (hàng 2): standard backline carry
- **Front-row middle** (hàng 0, cột 3-4): tank anchor
- **Flanks (cạnh)**: AoE threats, isolate burst

---

## 2. Zephyr / mirrored-hex counter

Zephyr banish enemy trên **mirrored hex** (mirror qua tâm (1.5, 3)):
- Carry ở (0,0) → đối thủ Zephyr target (3,6)
- Carry ở (3,6) → đối thủ Zephyr target (0,0)

**Counter**: 2 giây cuối planning phase, dời carry khỏi ô mirror của Zephyr đối thủ.

**Shroud of Stillness**: target 3 enemy xa nhất trong cone từ hex nó đứng. Mirror-shuffle counter giống hệt.

---

## 3. Diver / assassin counter

Divers (Khazix, Rengar — khi đối thủ chơi) nhảy vào **backline xa nhất hoặc HP thấp nhất**.

| Counter | How |
|---------|-----|
| **Clump carry + body** | Carry ở back row với 1 unit kề → diver landing vào frontline |
| **Spread + corner** | Carry 1 mình ở góc → diver phải đi qua frontline |
| **Bait corner** | Unit yếu nhất ở góc đối diện → kéo dive sang đó |

---

## 4. Formation templates

| Template | Shape | Use case |
|----------|-------|----------|
| **Y-shape** | 2 frontline đỉnh + funnel backline | Standard AoE-resistant |
| **Spread** | Full-width thin frontline | Giảm AoE cluster damage |
| **Wall** | 4 tank thẳng hàng | Melee stall comps |
| **Corner stack** | Carry + 1 unit kề ở góc | Anti-assassin |
| **Scatter** | Backline chia L/R corners | 2 AP carry, split focus |

---

## 5. Scouting workflow

Mỗi planning phase (ngân sách ~8 giây — engine chỉ cần <1ms):

1. **Identify next opponent** (xem §7)
2. **Check carry item set** → suy comp
3. **Check backline position** → mirror / flank accordingly
4. **Check for diver** (Khazix 2★+, Rengar 2★+) → clump hoặc bait
5. **Check trait panel** cho Executioner/Blossom/Eclipse power spike
6. **Decide position** trước khi timer < 5s

→ Engine làm hết việc này với memory read `<1ms/opponent`.

---

## 6. Threat assessment

```
threat_score(opponent) =
  board_damage_rating(items + traits)
+ 2★ count × 1.0
+ 3★ carry present × 3.0
+ 4-cost 2★ with BIS × 2.0
+ 5-cost presence × 2.5
+ augment_quality × 1.5
```

Highest threat opponent → priority counter-position round này, scout thêm round sau bất kể pairing probability.

---

## 7. Pairing algorithm (community reverse-engineered)

Luật pairing TFT (chuẩn pre-2021, vẫn roughly accurate):

| Alive players | Forbidden recent rounds |
|---------------|------------------------|
| 7 | 4 round trước |
| 6 | 3 round trước |
| 5 | 2 round trước |
| ≤4 | chỉ loại round liền trước |

**Ghost** = thay thế player đã bị loại. Ghost strength = board người đó khi chết.

Riot nói sẽ làm pairing less predictable → treat là **high probability nhưng không chắc chắn**. Narrow next-opponent xuống 2–3 candidate, prep cho threat cao nhất.

---

## 8. Positioning decision engine

```python
@dataclass
class PositioningDecision:
    unit_placements: dict[str, HexCoord]
    reasoning: str
    threats_considered: list[str]       # opponent ids

def decide_positioning(
    board: list[BoardSlot],
    bench: list[Unit],
    next_opponent: OpponentState,
    comp: Comp,
    meta: MetaDB,
) -> PositioningDecision:
    threats = analyze_threats(next_opponent)   # Zephyr/Shroud/divers

    # 1. Tank anchor front
    tanks = [u for u in board if u.role == "tank"]
    tank_positions = optimal_tank_line(tanks, next_opponent.frontline)

    # 2. Carry placement — avoid mirror of Zephyr/Shroud
    carry = comp.primary_carry
    forbidden_hexes = compute_mirror_hexes(threats.zephyr, threats.shroud)
    carry_hex = choose_safest(available_backline, forbidden_hexes, threats.divers)

    # 3. Supports — adjacent to carry if carry has aura, otherwise fill
    ...

    return PositioningDecision(unit_placements=..., reasoning=..., ...)
```

---

## 9. Hằng số

```python
GRID_ROWS = 4
GRID_COLS = 7
GRID_CENTER = (1.5, 3)

def mirror_hex(hex_coord):
    r, c = hex_coord
    return (3 - r, 6 - c)

CORNERS = [(0, 0), (0, 6), (3, 0), (3, 6)]
```
