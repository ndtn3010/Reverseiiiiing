# Reverseiiiiing

TFT (Teamfight Tactics) auto-player: live state reader + decision engine + optional input executor.

## Architecture

```
┌─ Input Sources (read-only) ─────────────────────────────┐
│                                                         │
│  Live Client API (127.0.0.1:2999)                       │
│    → gold, HP, stage, level, lobby                      │
│                                                         │
│  Screen Capture (mss) + CV (OpenCV + optional YOLO)     │
│    → shop units, bench, board positions, items          │
│    → opponent boards (scoreboard scroll)                │
│                                                         │
│  External MCP servers:                                  │
│    - tft-oracle          (static game data)             │
│    - GeLi2001/tft-mcp    (post-match history)           │
│                                                         │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─ State Model (pydantic) ────────────────────────────────┐
│  GameState { stage, gold, hp, level, shop[], bench[],   │
│              board[], items[], traits[], augments[],    │
│              opponents[] }                              │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─ Decision Engine ───────────────────────────────────────┐
│  Match current board → closest meta comp                │
│  Score: econ vs rolldown, positioning, items            │
│  Output: ranked Action[]                                │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─ Output Layer (one of three modes) ─────────────────────┐
│  COACH_ONLY  → overlay suggestions, user clicks         │
│  SEMI_AUTO   → overlay + hotkey confirm each action     │
│  FULL_AUTO   → win32 input injection (risk of ban)      │
└─────────────────────────────────────────────────────────┘
```

## Modules

- `capture/`   — screen grabber + Live Client HTTP poller
- `vision/`    — CV champion/item detector, template DB
- `state/`     — pydantic GameState models
- `meta/`      — patch scraper + meta comps DB (SQLite)
- `decision/`  — rule-based + LLM-assisted engine
- `executor/`  — pydirectinput + win32api action runner
- `overlay/`   — PyQt6 transparent always-on-top window
- `mcp_server/`— our own MCP server exposing live state + meta DB
- `utils/`     — logger, config loader, timing helpers

## Modes

Configured in `config/config.yaml`:

```yaml
mode: COACH_ONLY     # COACH_ONLY | SEMI_AUTO | FULL_AUTO
tick_hz: 2
hotkey_toggle: F8
hotkey_execute: F9   # SEMI_AUTO only
```

## Risk notice

Riot's Vanguard anti-cheat (kernel-level, mandatory since 2024) actively detects
input injection. `FULL_AUTO` mode is likely to result in account suspension or
hardware ban. `COACH_ONLY` and `SEMI_AUTO` are much lower risk but still not
sanctioned by Riot. Use on a secondary account you can afford to lose.

## Install

```bash
# Windows (needs win extras for executor)
pip install -e ".[win,vision,mcp]"

# Linux/Mac (dev only, no executor)
pip install -e ".[vision,mcp]"
```

## Run

```bash
# Patch/meta scraper (run nightly via Task Scheduler / cron)
reverseiii-scrape

# MCP server (for Claude Desktop / Cursor integration)
reverseiii-mcp

# Main overlay + executor
reverseiii --config config/config.yaml
```

## External MCP servers (plug these into Claude Desktop)

```json
{
  "mcpServers": {
    "tft-oracle":    { "command": "npx", "args": ["-y", "tft-oracle"] },
    "tft-history":   { "command": "npx", "args": ["-y", "mcp-server-tft"],
                       "env": { "RIOT_API_KEY": "...", "GAME_NAME": "...", "TAG_LINE": "..." } },
    "reverseiii":    { "command": "reverseiii-mcp" }
  }
}
```
