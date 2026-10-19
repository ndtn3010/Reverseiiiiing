# TFT — Econ Math (Deep Dive)

> Set 18 · Patch 18.4. Toàn bộ công thức kinh tế mà engine phải tính được.

---

## 1. Bảng lãi suất (Interest curve)

Luật: **+1g lãi mỗi 10g trong túi cuối round, cap +5g (tại 50g)**. Patch 18.4 không đổi.

| Bank | Interest | Marginal value |
|------|----------|----------------|
| 0–9 | 0 | phải lên 10g mới có lãi |
| 10–19 | +1 | 0 sau khi đạt 10 |
| 20–29 | +2 | 0 sau khi đạt 20 |
| 30–39 | +3 | 0 sau khi đạt 30 |
| 40–49 | +4 | 0 sau khi đạt 40 |
| **50+** | **+5 (cap)** | **0 mãi mãi sau 50g** |

### Rule "free spend above breakpoint"
Gold giữa 2 breakpoint tốn 0 lãi suất. Ở 54g, 4g đầu tiên tiêu **free**. Ở 59g, 9g đầu tiên tiêu free.
→ Engine phải ưu tiên tiêu xuống **đúng breakpoint hiện tại**, không tiêu sâu hơn.

---

## 2. Bảng streak

Cả win-streak lẫn loss-streak đều ăn cùng bảng. Có 2 variant lưu hành:

| Streak length | Variant A (TFT Ninja, Metabot) | Variant B (op.gg Set 18) |
|---------------|-------------------------------|--------------------------|
| 2 | +0 | +1 |
| 3 | +1 | +1 |
| 4 | +1 | +2 |
| 5 | +2 | +3 |
| 6+ | +3 | +3 |

**op.gg Set 18 mới nhất → mặc định Variant B**. Engine phải detect bằng cách quan sát 1 round delta với streak đã biết, rồi lock variant.

---

## 3. Mô hình income tổng

```
income(round) = base_round_gold          # 2/2/3/4/5 stage 1, flat 5 sau đó
              + interest(bank)           # 0..5
              + streak_bonus(streak)     # 0..3
              + win_bonus                # 1 nếu thắng PvP, 0 nếu thua
              + pve_drops                # orbs, components, gold piles
```

- **Income tối đa/round**: ~14g (streak full + lãi max + win + base)
- **Income tối thiểu**: ~5g (xen kẽ thắng/thua từ bank 0)
- **Delta qua 25 round**: 100–180g giữa người greedy econ và người flat spender

---

## 4. Luật 50g — khi nào phá

**Luật 50g**: hoard tới 50g nhanh nhất có thể. Lãi cap cộng dồn mỗi round sau đó. Phá luật tốn 5g/round vĩnh viễn.

### Phá 50g khi **bất kỳ** điều kiện sau fire:

| Trigger | Threshold |
|---------|-----------|
| HP critical | `hp < 30` và sẽ thua 2 round tiếp |
| Natural level + roll window | Stage 4-1/4-2 cho Fast 8 (planned break) |
| Giữ streak | Roll 2–5g tìm 1 unit để giữ win-streak ≥2g/round |
| Rolldown stabilization | Classic 4-5 → 5-1 roll tìm carry |
| Comp lock-in | 3★ carry 1/2-cost ở lv6/7 |

### Deficit threshold heuristic
```
phá 50g khi cost_of_dying > future_interest_gained
```
Nếu sẽ bị loại trong 3 round, future interest = 15g. 1 cú roll 15g cứu được → đúng. Engine phải có `rounds_to_elimination` estimator liên tục.

---

## 5. Econ patterns

| Pattern | Level pivot | Roll floor | Comp điển hình |
|---------|-------------|-----------|----------------|
| **Hyperroll** | Stay 4–5 | Roll về 0 ở 3-2 | 1-cost reroll kiểu cũ, hiếm ở Set 18 |
| **1c Reroll** | Stay 6 | 50g slow-roll | Solar Rapidfire Reroll |
| **3c Reroll** | Push 7 ở 3-5 | 50g slow-roll | Kha'Zix Reroll, Solar Kayle, Exec Azir slow |
| **Standard** | Lv8 ở 4-2/4-3, roll ~30–40g | 20g emergency floor | Defender Rengar, Spellweaver Rammus |
| **Fast 8** | Lv8 ở 4-1 | Roll về ~20g | Flora Fatalis Azir, Elder Dragon |
| **Fast 9** | Lv9 ở 5-1 | Dump hết ở 9 | Elderwood Draven, 5-cost hunt |

---

## 6. Econ-is-king vs Tempo-is-king

| Econ win khi | Tempo win khi |
|--------------|---------------|
| HP > 60 | HP < 50 |
| Board stable | Board leak |
| Comp không contested | Có win-streak sẵn |
| Setup slow-roll | Có item slammable (free top-4) |
| Chơi cho top 1 | Chỉ cần top-4 |

Engine score:
```
greed_tolerance = f(hp,
                    board_strength_delta_vs_lobby_avg,
                    streak_state,
                    planned_level_pivot)
```

---

## 7. Hằng số cho engine

```python
INTEREST_CAP = 5
INTEREST_PER = 10
STREAK_BONUS = {2: 1, 3: 1, 4: 2, 5: 3, 6: 3}  # Variant B default
BASE_INCOME_STAGE1 = [2, 2, 3]   # 1-1, 1-2, 1-3
BASE_INCOME = 5
WIN_BONUS = 1
GOLD_PER_INTEREST_UNIT = 10
MAX_INTEREST_BANK = 50
```
