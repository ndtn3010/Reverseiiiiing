# Analysis — TFT Auto-Player AI

Foundation docs. These feed the engine's rulebook and the scraper's targets.

| File | Topic |
|------|-------|
| [01-game-mechanics.md](./01-game-mechanics.md) | Round structure, econ, levels, shop odds, pool, items, Set 18 mechanics, state schema |
| [02-current-patch.md](./02-current-patch.md) | Set 18 / Patch 18.4 overview, patch 18.4 changes, scraper requirements, meta volatility, refresh schedule |
| [03-meta-comps.md](./03-meta-comps.md) | Current meta comps with carry/items/playstyle, matcher scoring, source confidence table |

## Headlines

- **Set 18 Enchanted Wilds** · Patch **18.4** · Set 19 lands **2026-12-01**
- **Wisps** replace charms — rightmost shop slot, every other round, planning phase only
- Current S/S+ comps: **Solar Kayle Reroll**, **Executioner Azir** (4.09 avg), **Defender Rengar** (4.14 avg), **Flora Fatalis Azir** (4.20 avg), **Riftbeast Elder Dragon**
- Memory-read provider is the plan — vision stays as fallback
- Set rollover on 2026-12-01 = **comp DB wipe**, not incremental refresh

## Sources

Research cross-referenced across: Riot official notes, TFT Sense, TFTSet.com, Esports.gg, Mobalytics, Blitz, SeeMeta, Emblem Comp, BunnyMuffins, La Casita del TFT, TFT Flow, TopMeta, TFT Ninja, Tapin.gg, Metabot, TFT Academy.
