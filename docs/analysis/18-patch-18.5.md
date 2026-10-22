# TFT — Patch 18.5 (2026-10-21)

> Live date: **2026-10-21**. Research pull 2026-10-22. Numbers low-confidence tới khi scraper verify client.

---

## 1. Headline

- **New Augment caps** (specifics chưa surface)
- **Riftbeast nerf** → directly hit Pebbles & Krug comp (S+ của 18.4)
- **Blackthorn 6-piece bonus** 60% → 50% → cap-chasing boards suffer
- **12+ unit buffs** → A-tier spread rộng hơn

---

## 2. Trait changes

| Trait | Change |
|-------|--------|
| **Blackthorn 6-piece** | Enhanced bonus **60% → 50%**, base AP sacrifice reduced |
| **Elderwood 9-piece summon** | Bonus HP **140% → 125%** |
| **Fae 2/4-piece heal** | Heal **2.5/4% → 3/5%** (buff) |
| **Rapidfire** | AS steps per attack reduced (nerf) |
| **Riftbeast** | AD/AP reduced (nerf) |
| **Flora Fatalis** | Max-HP healing **8% → 7%** (nerf) |

---

## 3. Champion changes

### Nerfed
| Champ | Change |
|-------|--------|
| **Azir** | Ability damage **46/69/110 AP → 43/65/105 AP** |
| **Kha'Zix** | Nerfed (specifics not surfaced) |

### Buffed (12 units — exact deltas chưa pull)
- Caitlyn
- Master Yi
- Tristana
- Brambleback
- Malphite
- Morgana
- Sett
- Sivir
- Soraka
- Alune
- Ashe
- Taric

### Trait/unit ambiguous
- **Sentinel** nerfed (unit hay trait — chưa rõ)

---

## 4. Wisp changes

| Wisp | Change |
|------|--------|
| **Hand of Baron** | Loses ~1/3 stats, price **6g → 4g** |

---

## 5. Item changes

| Item | Change |
|------|--------|
| **Radiant Adaptive Helm** | Nerfed |
| **Radiant Blue Buff** | Nerfed (was S+ tier 18.4) |

---

## 6. Meta impact prediction

| Comp | Prediction | Lý do |
|------|-----------|-------|
| Riftbeast Pebbles & Krug | **S+ → A** | Riftbeast AD/AP nerf trực tiếp |
| Executioner Azir | **S+ → S** | ~5-6% damage loss, vẫn viable |
| Flora Fatalis Azir | **S → A+** | Azir nerf + Flora heal nerf combo |
| Elderwood Draven | **A+ → A** | 9-piece summon HP cut 15% |
| Blackthorn comps | **A → B** | 6-piece bonus cut 10% là big |
| Solar Kayle | **S → S** | Không bị touch |
| Defender Rengar | **S → S** | Không bị touch |
| Fae comps | **B → A** | Heal buff 2.5→3% là significant trong early |

→ Buffs trên 12 unit → **lobby diversity cao hơn**, engine phải re-scrape meta comps sau 1 tuần settle.

---

## 7. Engine refresh action

```yaml
on_18_5_detected:
  priority_1:
    - update_trait_breakpoints:
        blackthorn: {6: {bonus_pct: 0.50}}
        elderwood: {9: {summon_hp_pct: 1.25}}
        fae: {2: {heal_pct: 0.03}, 4: {heal_pct: 0.05}}
    - update_champion_abilities:
        Azir: {damage: [43, 65, 105]}
    - update_wisp_prices:
        HandOfBaron: {price: 4, stats_mult: 0.67}
    - update_radiant_values:
        RadiantAdaptiveHelm: nerfed
        RadiantBlueBuff: nerfed

  priority_2:
    - mark_tier_dirty: [RiftbeastKrug, ExecAzir, FloraAzir, ElderwoodDraven, Blackthorn*]
    - schedule_recomp_after: 7_days   # chờ meta settle

  priority_3:
    - pull_full_patch_notes: riot_official_url
    - re_scrape_augment_catalog
    - re_scrape_wisp_catalog
```

---

## 8. Confidence levels

| Data | Confidence |
|------|-----------|
| Patch date | High (2026-10-21) |
| Trait numeric changes | Medium (2-source agreement) |
| Azir damage nerf exact numbers | Medium-low (1 source) |
| Buffed unit list | Low (name only, no deltas) |
| Hand of Baron change | Medium (1 source, specific numbers) |
| Meta tier shift | Low (data too fresh, <1 week since release) |
