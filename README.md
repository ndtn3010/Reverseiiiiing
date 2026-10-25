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

### End user (zero setup)

1. Download `reverseiii-windows.zip` from
   [latest release](https://github.com/ndtn3010/Reverseiiiiing/releases).
2. Extract anywhere.
3. Double-click `reverseiii.exe`.

That's it. First launch auto-downloads TFT assets from CommunityDragon
(champ icons, items, traits — ~30 MB), auto-detects your monitor
resolution, and starts the overlay. No Python, no Tesseract, no manual
screenshots required.

### Developer

```bash
# Windows (needs win extras for executor)
pip install -e ".[win,vision,mcp]"

# Linux/Mac (dev only, no executor)
pip install -e ".[vision,mcp]"
```

## Run

```bash
# One-time bootstrap (end-user .exe does this on startup automatically)
python -m reverseiiiiing.vision.bootstrap

# Main overlay + executor
reverseiii                         # auto-detects everything
reverseiii --refresh-assets        # force re-download after new patch
reverseiii --skip-bootstrap        # if offline

# Patch/meta scraper (nightly)
reverseiii-scrape

# MCP server (for Claude Desktop)
reverseiii-mcp
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
