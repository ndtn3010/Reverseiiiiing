"""Main entry point: wires capture → state → decision → executor/overlay."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from reverseiiiiing.capture.live_client import LiveClient
from reverseiiiiing.executor.hotkeys import HotkeyManager
from reverseiiiiing.executor.input_win import ExecutorConfig, InputExecutor
from reverseiiiiing.state.models import GameState
from reverseiiiiing.utils.config import load_config
from reverseiiiiing.utils.logger import get_logger

log = get_logger("reverseiii")


async def main_loop(cfg: dict) -> None:
    tick_s = 1.0 / cfg.get("tick_hz", 2)
    mode = cfg.get("mode", "COACH_ONLY")

    exec_cfg = ExecutorConfig(
        mode=mode,
        click_delay_ms=tuple(cfg["executor"]["click_delay_ms"]),
        move_duration_ms=tuple(cfg["executor"]["move_duration_ms"]),
        bezier_jitter=cfg["executor"]["bezier_jitter"],
    )

    try:
        executor = InputExecutor(exec_cfg, tuple(cfg["capture"]["resolution"]))
    except RuntimeError as e:
        log.warning(f"Executor unavailable: {e}. Running in dry-run.")
        executor = None

    hk = HotkeyManager()
    hk.bind(cfg["executor"]["hotkey_panic"],
            lambda: executor and executor.panic())
    hk.start()

    async with LiveClient(
        base_url=cfg["capture"]["live_client_url"],
        verify_ssl=cfg["capture"]["verify_ssl"],
    ) as live:
        log.info(f"Started in {mode} mode @ {cfg.get('tick_hz')} Hz")
        while True:
            snap = await live.snapshot()
            if not snap.running:
                log.info("No game detected; waiting…")
                await asyncio.sleep(2.0)
                continue

            # TODO: Tasks 4-6 fill these in
            state = GameState()
            # state = await screen_reader.read(state)
            # state = await meta.enrich(state)
            # actions = decision.plan(state)
            # if mode == FULL_AUTO: executor.execute(actions[0], coords)
            # elif mode == SEMI_AUTO: queue for F9 confirm
            # overlay.render(state, actions)

            await asyncio.sleep(tick_s)


def main() -> int:
    ap = argparse.ArgumentParser(prog="reverseiii")
    ap.add_argument("--config", default="config/config.yaml", type=Path)
    args = ap.parse_args()

    cfg = load_config(args.config)
    try:
        asyncio.run(main_loop(cfg))
    except KeyboardInterrupt:
        log.info("Exiting on ^C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
