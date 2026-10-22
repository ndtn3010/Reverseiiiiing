# TFT — Augment Decision Theory (Deep Dive)

> Chọn augment là 3 quyết định quan trọng nhất mỗi game (2-1, 3-2, 4-2).

---

## 1. Armory structure

| Round | Tier chính | Reroll |
|-------|-----------|--------|
| **2-1** | Silver (mostly), ít Gold | 1 free reroll (replace cả 3) |
| **3-2** | Gold (mostly), ít Prismatic | 1 free reroll |
| **4-2** | Prismatic (mostly), ít Gold | 1 free reroll |

Lưu ý: Set 18 chuẩn là **1 free reroll/armory**. Nguồn có bàn cãi (có nguồn nói 3) — mặc định 1.

---

## 2. Tier odds (baseline Set 16, verify Set 18)

| Armory | Silver | Gold | Prismatic |
|--------|--------|------|-----------|
| 2-1 | 28% | 62% | 10% |
| 3-2 | tùy pick 2-1 | majority | ~15–25% |
| 4-2 | low | ~30% | majority |

Mỗi tier cao hơn ~1.5–2x impact trung bình trên placement. **Prismatic > Gold > Silver** về raw power, nhưng **comp fit > tier**.

---

## 3. Augment categories

| Category | Timing payoff | Example 18.4 top |
|----------|---------------|------------------|
| **Combat** (trait, stat buffs) | Immediate mỗi fight | Dark Ritual (S, SeeMeta) |
| **Econ** | Compounds qua game | Explosive Growth (S), Branching Out (S), Bronze For Life II (S) |
| **Hero/Trait** (lock 1 champ làm carry) | Depends on hit | Epic Rolldown (S) |
| **Scaling** | Late-game cap | Baron's Lair (S), Booster Pack (S) |
| **Risk/Reward** | Variance | Golden Gamble (+22g, interest cap 10) |

---

## 4. Patch 18.4 top augments (SeeMeta S-tier)

- **Dark Ritual** (enables Coven reroll)
- **Epic Rolldown**
- **Explosive Growth** (post-nerf: 9 XP/round)
- **Baron's Lair**
- **Booster Pack**
- **Branching Out**
- **Bronze For Life II**

PBE 18.4 tier A: Prismatic Destiny / Prismatic Destiny+ / Prismatic Ticket, Gold Destiny / Gold Destiny+.

**Disabled 18.4 B-patch**: Heart of Steel (bug).

---

## 5. Scoring formula

```
score(aug) = tier_value[tier]                       # 1 / 2 / 3 for S/G/P
           + comp_synergy[aug, current_comp] × 2.0
           + econ_curve_value[aug, current_stage] × 1.0
           + scaling_potential[aug] × stage_remaining / 7
           + flex_value[aug] × 0.5                  # augment phục vụ bao nhiêu comp
```

### Reroll rule
Reroll khi `max(current 3) < expected(reroll)` — chỉ khi:
- Cả 3 option hiện tại off-comp HOÀN TOÀN, VÀ
- Tier trung bình dưới Prismatic (ở 4-2) hoặc Gold (ở 3-2)

---

## 6. Combat vs Econ tradeoff tại 2-1

**Chọn Econ augment** khi:
- Có plan comp cuối rõ ràng (muốn fast 8/9 hoặc slow-roll bùng ở lv7+)
- Build items chưa commit → cần gold để pivot
- Mục tiêu top-1

**Chọn Combat augment** khi:
- Có 2★ carry sớm cần buff ngay
- Trait augment match với 2★ unit đã có
- Mục tiêu top-4 chắc chắn

**Chọn Hero augment** khi:
- Hero augment là carry 4-cost và mình nghĩ sẽ hit được
- Hero augment thuộc comp đang được lobby ít contested

---

## 7. Augment-comp synergy table (một số case)

| Augment | Best comp | Mechanism |
|---------|-----------|-----------|
| Dark Ritual | Coven Elise reroll | Trait enabler |
| Epic Rolldown | Any fast-8/9 | Free rolldown value |
| Cursed Crown | +1 unit scaling comps (Solar Kayle 8 units ở lv6) | Trait breakpoint |
| Baron's Lair | Scaling AP comps | Late-game cap |
| Golden Gamble | Econ opener → aggressive | +22g = big tempo swing |

---

## 8. Engine integration

```python
@dataclass
class AugmentDecision:
    pick: Augment              # chọn cái nào trong 3
    reroll: bool               # có nên reroll không
    reroll_rationale: str

def choose_augment(
    options: list[Augment],
    state: GameState,
    comps: list[Comp],       # top-3 comps từ matcher
    meta: MetaDB,
) -> AugmentDecision:
    scored = [(aug, score(aug, state, comps, meta)) for aug in options]
    best, best_score = max(scored, key=lambda x: x[1])

    expected_reroll_score = meta.augment_tier_expected_value(state.round, options)
    if best_score < expected_reroll_score * 0.8:
        return AugmentDecision(pick=None, reroll=True, ...)

    return AugmentDecision(pick=best, reroll=False)
```

---

## 9. Hằng số

```python
TIER_VALUE = {"silver": 1, "gold": 2, "prismatic": 3}

ARMORY_SCHEDULE = {
    "2-1": "silver",
    "3-2": "gold",
    "4-2": "prismatic",
}

AUGMENT_TIER_ODDS = {
    "2-1": {"silver": 0.28, "gold": 0.62, "prismatic": 0.10},
    "3-2": {"silver": 0.10, "gold": 0.70, "prismatic": 0.20},
    "4-2": {"silver": 0.00, "gold": 0.30, "prismatic": 0.70},
}
```
