# Reverseiiiiing

TFT auto-player AI — meta scraper, memory provider, decision engine.

Target: Set 18 Enchanted Wilds · Patch 18.5.

## Repo layout

```
docs/analysis/      # 21 reference docs — game mechanics, patch, meta, combat math, scraper design
src/reverseiiiiing/
  meta/             # scraper + SQLite knowledge base (this phase)
  providers/        # game state readers (memory / vision / replay — later)
  engine/           # decision modules (later)
tests/              # pytest
config.yaml         # scraper + DB config
```

## Scraper CLI (phase 1)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]

rv init-db                 # create data/tft.db
rv probe                   # fetch CDragon payload summary, no DB write
rv refresh                 # pull CDragon + upsert champions/traits/items
rv status                  # table counts + latest patch
rv inspect champions --cost 5
rv inspect traits
rv inspect items --limit 20
```

Network required: `raw.communitydragon.org` (no auth, no rate limit).

## Status

- Phase 1 scraper: foundation shipped (CDragon puller, patch detection, SQLite schema, CLI).
- Phase 1 extensions: augments / wisps / comps scrapers (SeeMeta + Metabot + Mobalytics) — not yet.
- Phase 2 memory provider: not yet.
- Phase 3 decision engine: not yet.

## Analysis docs

See [docs/analysis/README.md](docs/analysis/README.md) for the full index.

Highlights:
- Econ math, rolldown probability, leveling, carousel, augments, positioning, Set 18 depth, match flow
- Combat math (damage formula, mana generation, AS cap, end-of-round damage)
- Champion/item/trait exact numbers
- Patch 18.4 + 18.5 deltas
- Scraper endpoints + SQLite schema
