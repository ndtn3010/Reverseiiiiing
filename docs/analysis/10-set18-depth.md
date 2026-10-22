# TFT — Set 18 Specific Mechanics (Deep Dive)

> Wisps, Blossom, Elderwood, Blackthorn, Solar/Lunar/Eclipse. Những cơ chế riêng Set 18.

---

## 1. Wisps — cơ chế chính

### Cơ bản
- **Spawn**: slot bên phải shop **mỗi 2 round** 1 lần, chỉ **planning phase**
- **1 Wisp/round** mặc định; 2/round khi Blossom 9
- Single-use purchase
- Total: ~173–200 Wisps across 7 categories (nguồn khác nhau)

### Categories

| Category | Hiệu ứng |
|----------|---------|
| **Combat** | Buff team cho fight này thôi |
| **Economy** | Gold hoặc XP |
| **Shop** | Reroll / odds manipulation |
| **Items** | Components hoặc completed |
| **Champions** | Free units |
| **Risk/Reward** | Gamble effects |

### Rule mới sau stage 5
Mỗi alternate Wisp **guaranteed Combat tier** → late-game variance tightens.

### Patch 18.4 Wisp price cuts
- **Cutpurse**: 3g → 2g
- **Slow Study**: 4g → 2g
- **Search Party**: 3g/1g → 1g/0g
- 4 free Wisps thêm vào low-gold shops
- Polymorph Wisps limited to first 2 seconds of planning phase
- Mua Wisp không chặn lên level (18.2 change still in effect)

---

## 2. Wisp EV framework

```
buy_wisp if:
    category == "econ" and payback_rounds <= remaining_rounds
    or category == "shop" and currently_rolling_for_3star
    or category == "combat" and this_fight_decides_elimination
    or price == 0
```

### Always-buy
- **Experienced** (XP deal; XP tốt nhất game khi lên level ở stage 2)
- Bất kỳ **free Wisp** stage 2 (Coin Flip, Truce)
- **Shop Wisps** khi đang 50g+ slow-roll

### Situational
- **Cutpurse** (2g post-18.4): gold sớm, opener tốt
- **Slow Study** (2g post-18.4): XP per surviving champion, mạnh trên board win-streak
- **Payday / Roly-Polys**: gold per surviving champion

### Usually skip
- Combat Wisp giá trung bình trên fight mình đã chắc thắng
- Risk/reward khi HP khỏe (variance không add value)

### Trait prerequisite
**Spirit Blossom squad** (Blossom cao) → ăn full Wisp value, có thể greed Wisp mỗi round.

---

## 3. Blossom trait (interact trực tiếp với Wisps)

| Breakpoint | Hiệu ứng |
|-----------|---------|
| **3** | Wisps upgraded (base tier → +) |
| **5** | Wisps appear trong **every shop** |
| **7** | **+gold khi mua Wisp** |
| **9** | **Buy 2 Wisps/round** |
| **11** | Wisps overflow |

### Blossom greed window
Khi Blossom 7 fire → **buy mọi Wisp mỗi round**. Pay-back accelerate.
Blossom 9 → buy 2/round.
Nhiều board cap-chasing Set 18 ride Blossom tới 9 rồi pivot ra khỏi 7-Blossom (board cap cao hơn ở 5-Blossom + traits khác).

### Blossom champions
Karma, Yorick, Yunara, Master Yi, Ahri, Sett, Ashe.

---

## 4. Elderwood plants

| Field | Value |
|-------|-------|
| Breakpoints | 3 / 5 / 7 / 9 / 11 |
| Mechanic | Spawn **plants** làm board entities thêm |
| Plant stats | Scale Max HP + AP theo Elderwood Star Level |
| Max plants | Scale với trait level (nguồn chưa confirm exact count) |

→ Engine phải track plant entities như unit riêng khi tính board damage.

---

## 5. Blackthorn sacrifice

| Field | Value |
|-------|-------|
| Breakpoints | 2 / 4 / 6 |
| Mechanic | Pre-combat **sacrifice ally trên Blackthorn hex** → team gain HP |
| Values | Blitz 2 tiers: 175 / 350. tftraits 3 tiers: 175 / 350 / 600 |

### Sacrifice math
```
sacrifice_value = gained_team_hp - sacrificed_unit_board_contribution
```

Sacrifice tốt khi:
- Unit sacrificed là 1-cost bench, HOẶC
- Unit redundant trên board (không activate trait quan trọng)
- Engine chọn unit DPS thấp nhất trên Blackthorn hex

Blackthorn champs: Rek'Sai, Veigar, Warwick, Azir, Malphite.

---

## 6. Solar / Lunar / Eclipse

### Solar
- Breakpoint 3 + per-3★ milestones
- Shielding + magic damage
- Reward 3★ boards

### Lunar
- AS + AP cho Lunar champs + adjacent allies

### Eclipse (hidden trait)
- Activate khi **Solar(3) + Lunar(3) đồng thời**
- Patch 18.4: Eclipse fire **8s vào combat**, repeat **mỗi 3.5s**
- Riot công nhận early executes "feel weak" ở 18.4

### Standard Eclipse comp
Kayle, Aphelios, Sejuani — reroll 3★s rồi push level cho Lunar(3), có thể cân nhắc Lunar Emblem.

---

## 7. Trait highlights khác

| Trait | Breakpoints | Mechanic |
|-------|-------------|----------|
| **Elderwood** | 3/5/7/9/11 | Plants trên board |
| **Fae** | — | Attracts **Pixies** (companion units) |
| **Solar / Lunar** | — | Pair unlocks hidden **Eclipse** |
| **Blackthorn** | 2/4/6 | Sacrifice ally on hex |
| **Brawler** | 2/4/6 | Team max HP, Brawlers more |
| **Rapidfire** | 2/3/4/5 | Attack speed |

Signature traits (single-champ): Ivern, Maokai, Zyra.

---

## 8. Engine integration

```python
@dataclass
class WispDecision:
    buy: bool
    reasoning: str
    payback_rounds: int | None
    opportunity_cost: int   # gold forgone from interest

def evaluate_wisp(
    wisp: Wisp,
    state: GameState,
    comp: Comp,
    rounds_remaining_estimate: int,
) -> WispDecision:
    if wisp.price == 0:
        return WispDecision(buy=True, reasoning="free")
    if wisp.category == "econ":
        payback = wisp.expected_value(state) / state.income_per_round
        if payback <= rounds_remaining_estimate:
            return WispDecision(buy=True, payback_rounds=payback, ...)
    if wisp.category == "combat" and state.hp < 30:
        return WispDecision(buy=True, reasoning="elimination risk")
    if wisp.category == "shop" and state.rolling_for_3star:
        return WispDecision(buy=True, reasoning="rolldown enabler")
    if state.has_trait("blossom", 7) and state.gold > wisp.price + 50:
        return WispDecision(buy=True, reasoning="blossom greed window")

    return WispDecision(buy=False, reasoning="opportunity cost too high")
```

---

## 9. Encounters & Portals

Cả 2 return ở Set 18 nhưng specifics mỏng trong nguồn.
→ Engine expose `encounter_event: str | None` trong state, **không hardcode outcomes**.
Load từ Riot static data tại startup.
