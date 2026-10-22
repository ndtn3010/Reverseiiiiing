# TFT — Level Up Timing (Deep Dive)

> Level quyết định board size và shop odds. Khi lên lv là quyết định quan trọng mỗi stage.

---

## 1. XP curve (Set 18, post-18.2)

Patch 18.2 cắt cost 7→8, 8→9, 9→10 mỗi cái 4 XP.

| Level | XP to next | Gold cost (full buy) | Natural rounds (2 XP free/round) |
|-------|------------|----------------------|----------------------------------|
| 1 → 2 | 2 | 2 | 1 |
| 2 → 3 | 2 | 2 | 1 |
| 3 → 4 | 6 | 6 | 3 |
| 4 → 5 | 10 | 10 | 5 |
| 5 → 6 | 20 | 20 | 10 |
| 6 → 7 | 36 | 36 | 18 |
| 7 → 8 | **56** (was 60) | 56 | 28 |
| 8 → 9 | **64** (was 68) | 64 | 32 |
| 9 → 10 | **64** (was 68) | 64 | 32 |

- XP buy: **4 XP / 4g**
- End-of-round free: **2 XP**

---

## 2. Natural level timings (chỉ XP free)

| Round | Natural level |
|-------|---------------|
| 1-1 | 1 (start) |
| 2-1 | **4** (automatic — luôn lên, free) |
| 2-5 | 5 |
| 3-2 | 6 |
| 3-5 / 4-1 | 7 |
| 4-1 / 4-2 | **8** rolldown window |
| 5-1 / 5-2 | 9 (standard tempo) |
| 6-x | 10 |

→ Người chơi không mua XP sẽ đi theo đường này. Fast 8 = push sớm hơn natural.

---

## 3. Decision tree level 8

| Round | HP | Gold | Board | Decision |
|-------|-----|------|-------|----------|
| 4-1 | ≥60 | ≥50 | mạnh | **Fast 8**, roll về ~20g tìm 4c carry |
| 4-2 | 40–60 | 30–50 | ok | Standard 8 sau Gold augment, roll ~25–30g |
| 4-3 | 30–40 | ~30 | leak | Lên lv rồi roll về ~15g, slam items |
| 4-5 | <30 | any | sắp chết | Lv8 ở 4-5 và dump — stabilize or lose |

---

## 4. Fast 9 feasibility

Để push Fast 9 (ví dụ Elderwood Draven), cần **đủ cả 2**:
- **HP ≥ 50 ở 5-1** (survival margin)
- **Gold ≥ 50 ở 5-1 sau khi đã lên 8**, HOẶC
- **Gold ≥ 65 ở 5-1** để lên 9 luôn (64 XP + 1 buffer)
- Lv8 board mạnh (2★ 4-cost đầy đủ, không có lỗ hổng) để win-streak qua 5-1 trong lúc econ

### Minimum gold để lên lv9 từ lv8 bằng buy
- Nếu đã có 56 XP banked ở lv8 (natural tới 8 ở 4-2) → cần thêm 8 XP = 2 lần buy = **8g**
- Thực tế player push Fast 9 cần bank 50g+ trước khi lên 9 để còn roll 5-cost

---

## 5. Forced level cases

Engine phải force level kể cả không đạt gold ideal:
- **Không chơi được 8 unit ở lv7**: lên luôn nếu unit thứ 8 đã 2★ và mạnh
- **Trait breakpoint cần 1 unit**: lên nếu breakpoint mở ≥15% board power
- **Augment yêu cầu level**: Cursed Crown, hero augments pinned level
- **5-cost hunt**: lên lv9 bất kể HP khi đã stabilize top-4

---

## 6. XP cost model

```
xp_cost_to_level(current_lv, target_lv, current_xp):
    xp_needed = sum(XP_TO_NEXT[lv] for lv in range(current_lv, target_lv)) - current_xp
    buys_needed = ceil(xp_needed / 4)
    return buys_needed * 4   # gold
```

Ví dụ: ở lv7 với 20 XP banked, muốn lên lv8:
- XP cần = 56 − 20 = 36
- Buys = 9
- Gold = **36g**

Nhưng mỗi round có 2 XP free, nên nếu không gấp, chờ 1 round = tiết kiệm 2g.

---

## 7. Engine decision function

```python
def should_level_up(state: GameState, comp: Comp) -> LevelDecision:
    # Fast comps
    if comp.playstyle == "fast_8" and state.round == "4-1":
        return LevelDecision("level", target_lv=8, cost=xp_cost(state, 8))
    if comp.playstyle == "fast_9" and state.round == "5-1" and state.gold >= 50:
        return LevelDecision("level", target_lv=9, cost=xp_cost(state, 9))

    # Reroll comps — stay
    if comp.playstyle in ("1c_reroll", "3c_reroll"):
        if state.level < comp.level_pivot:
            return LevelDecision("level", target_lv=comp.level_pivot)
        return LevelDecision("hold")

    # Standard
    if state.hp < 30 and state.level < 7:
        return LevelDecision("level", target_lv=state.level + 1)
    if state.gold >= 50 + xp_cost(state, state.level + 1):
        return LevelDecision("level", target_lv=state.level + 1)

    return LevelDecision("hold")
```
