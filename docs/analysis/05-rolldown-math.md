# TFT — Rolldown Probability (Deep Dive)

> Xác suất trúng tướng khi roll. Toàn bộ công thức engine cần để quyết định roll hay giữ.

---

## 1. Pool size (Set 18)

Pool share toàn lobby — mỗi copy đối thủ cầm làm giảm tỷ lệ của mình.

| Cost | Copies/champ | Distinct champs | Total pool |
|------|--------------|-----------------|------------|
| 1 | 30 | 14 | 420 |
| 2 | 25 | 13 | 325 |
| 3 | 18 | 14 | 252 |
| 4 | 10 | 14 | 140 |
| 5 | 9 | 10 | 90 |

---

## 2. Shop odds (Set 18)

Mỗi shop refresh = 5 slot độc lập, mỗi slot roll theo bảng dưới.

| Lv | 1c | 2c | 3c | 4c | 5c |
|----|----|----|----|----|-----|
| 1 | 100 | 0 | 0 | 0 | 0 |
| 2 | 100 | 0 | 0 | 0 | 0 |
| 3 | 75 | 25 | 0 | 0 | 0 |
| 4 | 55 | 30 | 15 | 0 | 0 |
| 5 | 45 | 33 | 20 | 2 | 0 |
| 6 | 30 | 40 | 25 | 5 | 0 |
| **7** | 19 | 30 | **43** | 8 | 0 |
| **8** | 15 | 20 | 32 | **30** | 3 |
| 9 | 10 | 15 | 25 | 35 | 15 |
| 10 | 5 | 10 | 20 | 40 | 25 |
| 11 | 1 | 2 | 12 | 50 | 35 |

**Peaks**:
- Lv7 = 43% 3-cost → slow-roll 3c
- Lv8 = 30% 4-cost → rolldown 4c
- Lv11 = 35% 5-cost → săn legendary

---

## 3. Công thức xác suất hit

### Per-slot
Target T, cost C:
```
P(T trong 1 slot) = odds[level][C] × (copies_T_còn / tổng_copies_cost_C_còn)
```

### Per-shop (5 slot)
```
P(≥1 T mỗi shop) = 1 − (1 − P_per_slot)^5
```
(bỏ qua intra-shop depletion, sai số nhỏ)

### Per N roll
```
P(≥1 T trong N roll) = 1 − (1 − P_per_shop)^N
```

### Với pool depletion (chính xác)
Không có closed-form. Dùng Monte Carlo:
- Mỗi slot draw tạm thời xoá copy đã thấy
- Buy → xoá vĩnh viễn khỏi pool
- Chạy 10k simulation → xác suất hit expected

→ Engine cần `rolldown_simulator.py` với MC.

---

## 4. Expected copies để 3★ (uncontested, roll level lý tưởng)

| Cost | Roll level | Gold expected để 3★ (có 2–3 natural) |
|------|-----------|---------------------------------------|
| 1c | 6 | ~30–50g |
| 2c | 6 | ~40–60g |
| 3c | **7** | ~60–80g (standard 50g slow-roll) |
| 4c | **8** | 3★ không thực tế; mục tiêu 2★ với 20–40g |
| 5c | 9/10 | Chỉ 2★; 3★ cần augment hoặc hyperroll edge |

---

## 5. Contestedness math (CỰC KỲ QUAN TRỌNG)

Mỗi copy đối thủ cầm trừ thẳng khỏi pool share → tỷ lệ hit scale **tuyến tính**.

### Ví dụ cụ thể (TFT-Coaching)
Roll 100g tìm 4-cost ở lv8:
- 0 contested → ~**83%** hit ≥1 copy
- 5 copies bị cầm → ~**30%** hit

### Công thức
```
contest_multiplier = (copies_còn_trong_pool / copies_baseline)
P_adjusted = P_baseline × contest_multiplier
```

### Pivot rule
| Comp type | Threshold pivot |
|-----------|----------------|
| 4c/5c carry chưa có | `contest_multiplier < 0.5` → **pivot** |
| 1c/2c reroll | `contest_multiplier < 0.4` → pivot |
| 3c reroll | `contest_multiplier < 0.4` hoặc là người thứ 3 contested → pivot |

---

## 6. Roll floors (ngưỡng gold tối thiểu khi roll)

| Tình huống | Floor |
|-----------|-------|
| Emergency (sắp chết) | **10–20g** — roll tìm bất kỳ board hợp lệ |
| Standard lv8 rolldown | **~35g** — community minimum |
| Fast 8 planned | **~50g** push → roll về ~20g |
| Slow-roll @ 6/7 | **≥50g luôn** — chỉ roll phần dư trên 50 |
| Fast 9 | Dump hết gold khi đạt 9 |

---

## 7. Abandonment criteria (bỏ reroll comp)

Bỏ reroll comp khi **bất kỳ**:
- 50g+ đã tiêu, còn thiếu 2+ copy carry, bị contested bởi ≥2 người
- HP ≤ 35 và không có 3★ trong 2 roll tiếp theo (`P_hit < 60%`)
- Augment pivot (prismatic ticket, hero augment) cho carry khác cap cao hơn

---

## 8. Pool state tracking

Memory read cho pool state trực tiếp. Vision mode phải estimate từ:
- Scoreboard portraits (visible champs của 7 opponents)
- Shop history (tướng đã thấy trong shop của mình)
- Pool_remaining[champ_id] = total_pool − sum(all_visible_copies)

Engine cần `pool_tracker.py`:
```python
class PoolTracker:
    def __init__(self, patch_data):
        self.pool = {champ_id: POOL_SIZES[cost] for champ_id, cost in patch_data}

    def observe(self, opponent_id, board, bench):
        # cập nhật copies visible
        ...

    def contest_multiplier(self, champ_id):
        return self.pool_remaining[champ_id] / POOL_SIZES[cost_of(champ_id)]

    def hit_probability(self, champ_id, level, gold):
        n_rolls = gold // 2
        return monte_carlo_hit(champ_id, level, n_rolls, self.pool_remaining)
```

---

## 9. Decision output

Engine trả về mỗi round:
```python
@dataclass
class RollDecision:
    action: Literal["roll", "level", "hold", "slam"]
    target_champs: list[str]
    expected_cost: int           # gold expected
    hit_probability: float       # 0..1
    confidence: float            # based on contest_multiplier
    reasoning: str               # human-readable để UI hiện
```
