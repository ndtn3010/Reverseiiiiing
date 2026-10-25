"""Main entry point: wires capture → vision → decision → executor/overlay."""
from __future__ import annotations

import argparse
import asyncio
import sys
import threading
from pathlib import Path

from reverseiiiiing.capture.live_client import LiveClient
from reverseiiiiing.capture.screen import ScreenCapture
from reverseiiiiing.decision.engine import DecisionEngine, EngineConfig
from reverseiiiiing.executor.hotkeys import HotkeyManager
from reverseiiiiing.executor.input_win import ExecutorConfig, InputExecutor
from reverseiiiiing.mcp_server.server import CACHE
from reverseiiiiing.state.models import GameState
from reverseiiiiing.utils.config import load_config
from reverseiiiiing.utils.logger import get_logger
from reverseiiiiing.vision.detector import DetectorConfig, VisionDetector

log = get_logger("reverseiii")


class App:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.mode = cfg.get("mode", "COACH_ONLY")
        self.tick_s = 1.0 / cfg.get("tick_hz", 2)
        self._pending_action = None

        res = tuple(cfg["capture"]["resolution"])
        self.screen = ScreenCapture(monitor=cfg["capture"]["monitor"])
        self.detector = VisionDetector(
            DetectorConfig(
                template_dir=Path(cfg["vision"]["template_dir"]),
                champ_match_threshold=cfg["vision"]["champ_match_threshold"],
            ),
            actual_resolution=res,
        )
        self.engine = DecisionEngine(EngineConfig(
            comp_match_min_score=cfg["decision"]["comp_match_min_score"],
            risk_tolerance=cfg["decision"]["risk_tolerance"],
        ))

        try:
            self.executor = InputExecutor(
                ExecutorConfig(
                    mode=self.mode,
                    click_delay_ms=tuple(cfg["executor"]["click_delay_ms"]),
                    move_duration_ms=tuple(cfg["executor"]["move_duration_ms"]),
                    bezier_jitter=cfg["executor"]["bezier_jitter"],
                ),
                screen_resolution=res,
            )
        except RuntimeError as e:
            log.warning(f"Executor unavailable ({e}); COACH_ONLY only.")
            self.executor = None

        self.overlay = None
        self._init_overlay()

        self.hk = HotkeyManager()
        self.hk.bind(cfg["executor"]["hotkey_panic"], self._panic)
        self.hk.bind(cfg["executor"]["hotkey_execute"], self._confirm_execute)
        self.hk.bind(cfg["executor"]["hotkey_toggle"], self._toggle_overlay)
        self.hk.start()

    def _init_overlay(self) -> None:
        try:
            from PyQt6.QtWidgets import QApplication
            from reverseiiiiing.overlay.window import OverlayWindow
            # Run Qt in a background thread; main loop stays asyncio.
            def _run():
                self._qt_app = QApplication(sys.argv)
                self.overlay = OverlayWindow(self.mode)
                self.overlay.place_top_right(self.cfg["capture"]["resolution"][0])
                self.overlay.show()
                self._qt_app.exec()
            t = threading.Thread(target=_run, daemon=True)
            t.start()
        except ImportError:
            log.warning("PyQt6 not available; running without overlay.")

    def _panic(self) -> None:
        if self.executor:
            self.executor.panic()

    def _toggle_overlay(self) -> None:
        if self.overlay:
            self.overlay.setVisible(not self.overlay.isVisible())

    def _confirm_execute(self) -> None:
        if self.mode != "SEMI_AUTO" or not self._pending_action or not self.executor:
            return
        # TODO: build real screen_coords from detector anchors
        self.executor.execute(self._pending_action, screen_coords={})
        self._pending_action = None

    async def tick(self, live: LiveClient) -> None:
        snap = await live.snapshot()
        if not snap.running:
            return

        frame = self.screen.grab()
        state = self.detector.read_state(frame, GameState())
        actions = self.engine.plan(state)

        CACHE.set(state)

        if self.overlay:
            self.overlay.render(state, actions)

        if self.mode == "FULL_AUTO" and self.executor and actions:
            # TODO: real coords from anchor table
            self.executor.execute(actions[0], screen_coords={})
        elif self.mode == "SEMI_AUTO" and actions:
            self._pending_action = actions[0]

    async def run(self) -> None:
        log.info(f"Started in {self.mode} mode @ {1/self.tick_s:.1f} Hz")
        async with LiveClient(
            base_url=self.cfg["capture"]["live_client_url"],
            verify_ssl=self.cfg["capture"]["verify_ssl"],
        ) as live:
            while True:
                try:
                    await self.tick(live)
                except Exception as e:
                    log.exception(f"Tick failed: {e}")
                await asyncio.sleep(self.tick_s)


def main() -> int:
    ap = argparse.ArgumentParser(prog="reverseiii")
    ap.add_argument("--config", default="config/config.yaml", type=Path)
    args = ap.parse_args()

    cfg = load_config(args.config)
    app = App(cfg)
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        log.info("Exiting on ^C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
