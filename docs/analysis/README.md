# Analysis — TFT Auto-Player AI

Tài liệu nền tảng cho engine quyết định của bot. Mỗi file là 1 reference manual sâu, không phải guide bình thường.

## Files

| File | Nội dung |
|------|---------|
| [01-game-mechanics.md](./01-game-mechanics.md) | Round structure, econ, levels, shop odds, pool, items, Set 18 mechanics, state schema |
| [02-current-patch.md](./02-current-patch.md) | Set 18 / Patch 18.4 overview, scraper requirements, meta volatility, refresh schedule |
| [03-meta-comps.md](./03-meta-comps.md) | Current meta comps với carry/items/playstyle, matcher scoring, source confidence |
| [04-econ-math.md](./04-econ-math.md) | Interest curve, streak bonus, luật 50g, deficit threshold, econ patterns |
| [05-rolldown-math.md](./05-rolldown-math.md) | Pool/odds table, hit probability formula, contestedness math, roll floors, abandon rules |
| [06-leveling.md](./06-leveling.md) | XP curve, natural level timings, lv8 decision tree, Fast 9 feasibility |
| [07-carousel-items.md](./07-carousel-items.md) | Pick order, component priority, slam rules, radiant/artifact ranking |
| [08-augments.md](./08-augments.md) | Armory structure, tier odds, scoring formula, 18.4 top S-tier augments |
| [09-positioning.md](./09-positioning.md) | Hex grid, Zephyr/Shroud counter, diver counter, scout workflow, threat scoring |
| [10-set18-depth.md](./10-set18-depth.md) | Wisps + EV math, Blossom greed, Elderwood plants, Blackthorn sacrifice, Eclipse |
| [11-match-flow.md](./11-match-flow.md) | Round-by-round checklist, critical decision rounds, example lines, opponent reading |
| [12-combat-math.md](./12-combat-math.md) | Damage pipeline, armor/MR formula, mana generation, AS cap, crit stacking, end-of-round damage |
| [13-champion-stats.md](./13-champion-stats.md) | 9 top carry: stats base + ability + BIS (Azir, Kayle, Rengar, Draven, Kha'Zix, Elder Dragon, Elise, Nidalee, Veigar) |
| [14-item-stats.md](./14-item-stats.md) | Carry/tank item stats chính xác, radiants, uniqueness rules, BIS lookup table |
| [15-trait-numbers.md](./15-trait-numbers.md) | Blossom/Elderwood/Blackthorn/Eclipse/Executioner/Defender/Fae exact values |
| [16-hidden-mechanics.md](./16-hidden-mechanics.md) | Targeting, pathfinding, mana lock, dodge, untargetable, summons, overcap, combat sim stub |
| [17-patch-18.4-deltas.md](./17-patch-18.4-deltas.md) | Patch 18.4 exact deltas, B-patch changes, scraper refresh workflow, confidence levels |
| [18-patch-18.5.md](./18-patch-18.5.md) | **NEW** Patch 18.5 (2026-10-21): trait/champion/wisp/item changes, meta prediction |
| [19-encounters.md](./19-encounters.md) | Set 18 encounters (Kayle/Ashe/Draven/Teemo/Karma/Kobuko/Ornn/Lux/Yunara/Vi) + comp scoring |
| [20-scraper-targets.md](./20-scraper-targets.md) | CDragon + Riot API + meta-site URLs, scheduler config, initial SQLite schema |
| [21-pve-rounds.md](./21-pve-rounds.md) | PvE round composition (Krugs/Wolves/Raptors/Dragon), drop expectations, opener planning |

## Headlines

### Set
- **Set 18 Enchanted Wilds** · Patch **18.5** (2026-10-21) · Set 19 lands **2026-12-01**
- **Wisps** = cơ chế chính, rightmost shop slot mỗi 2 round, planning phase only

### Econ
- Interest cap +5g @ 50g — compound mỗi round
- Streak bonus up to +3g (Variant B: op.gg Set 18)
- Phá 50g khi `cost_of_dying > future_interest_gained`

### Rolldown
- Lv7 = peak 3-cost (43%), Lv8 = peak 4-cost (30%)
- Pool contestedness scale tuyến tính: 5 copies bị cầm = tỷ lệ hit từ 83% → 30%
- Pivot khi `contest_multiplier < 0.5` cho 4c/5c carry

### Current meta S/S+
- **Executioner Azir** (4.09 avg place)
- **Defender Rengar** (4.14 avg)
- **Flora Fatalis Azir** (4.20 avg)
- **Solar Kayle Reroll**, **Solar Rapidfire Reroll**, **Riftbeast Elder Dragon**

### Patch philosophy
- 18.4 shift power **traits → individual units**
- No roster/breakpoint changes, ~22 champions retuned
- B-patch 2026-10-08: Heart of Steel disabled, 7 units buffed

## Engine integration summary

Mỗi file trong analysis map thẳng vào 1 module trong `src/engine/`:

| Analysis doc | Engine module |
|--------------|---------------|
| 04-econ-math | `engine/econ.py` |
| 05-rolldown-math | `engine/rolldown.py` + `engine/pool_tracker.py` |
| 06-leveling | `engine/leveling.py` |
| 07-carousel-items | `engine/carousel.py` + `engine/items.py` |
| 08-augments | `engine/augments.py` |
| 09-positioning | `engine/positioning.py` + `scout/opponent.py` |
| 10-set18-depth | `engine/wisps.py` + `engine/set18_traits.py` |
| 11-match-flow | `engine/orchestrator.py` (state machine) |

## Sources (consolidated)

**Econ + rolldown**: Noxu, Metabot, TFT Ninja, Rankforge, Boosteria, LoL Wiki, op.gg, Tapin, SeeMeta, EsportsTales, TFT Sense, Frobei (Tacter), TFT-Coaching

**Leveling**: Noxu, TFT Ninja, TFT Sense, TopMeta, TFT Lab, Bamboo Gaming, Overgear, Metabot

**Carousel + items**: TFT Ninja, Yelzkizi, Mobalytics, Noxu, SeeMeta, Metabot, TFT Item Guide, Level Legendary, Boosteria, TFT School, Tapin

**Augments**: SeeMeta, Mobalytics, LeagueOfGraphs, TopMeta, Blitz, TFTFlow, Metabot, LoL Fandom

**Positioning**: Metabot, TFT Ninja, Noxu, Tapin, TFT School, Level Legendary, Mobalytics, EloBoost24

**Set 18 traits + Wisps**: Blitz, tftactics.gg, TFT Sense, tftraits, TFTFlow, Mobalytics, Blitz Eclipse, TopMeta Wisps, Riftdaily, Noxu, op.gg Set 18

**Patch 18.4 + meta**: Riot Official, Riftdaily, Blitz, TFT Sense, BunnyMuffins, SeeMeta, TFT Flow, Emblem, Mobalytics, TFT Academy
