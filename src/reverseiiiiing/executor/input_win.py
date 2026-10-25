"""Win32 input executor with randomized timing + bezier mouse curves.

MODES:
  - SEMI_AUTO: executes one action per hotkey press
  - FULL_AUTO: executes all actions in queue on tick

Timing jitter is intentional — straight-line, fixed-speed, pixel-perfect clicks
are the easiest signal for behavioral anti-cheat. We don't claim this defeats
Vanguard; we only make casual detection harder.

Panic key immediately disables input dispatch for the session.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass

try:
    import pydirectinput  # type: ignore
    pydirectinput.FAILSAFE = True
except ImportError:  # pragma: no cover
    pydirectinput = None  # type: ignore

from reverseiiiiing.state.models import Action
from reverseiiiiing.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class ExecutorConfig:
    mode: str = "COACH_ONLY"             # COACH_ONLY | SEMI_AUTO | FULL_AUTO
    click_delay_ms: tuple[int, int] = (60, 180)
    move_duration_ms: tuple[int, int] = (120, 320)
    bezier_jitter: bool = True


class InputExecutor:
    """Thin win32 wrapper. Does NOT make policy decisions — just does what Action says."""

    def __init__(self, cfg: ExecutorConfig, screen_resolution: tuple[int, int]):
        self.cfg = cfg
        self.res = screen_resolution
        self._enabled = cfg.mode != "COACH_ONLY"
        if self._enabled and pydirectinput is None:
            raise RuntimeError("pydirectinput required for SEMI_AUTO/FULL_AUTO. "
                               "pip install reverseiiiiing[win]")

    def panic(self) -> None:
        """Immediate kill switch; irreversible for session."""
        self._enabled = False
        log.warning("Executor panic-disabled")

    # --- public API ---------------------------------------------------------

    def execute(self, action: Action, screen_coords: dict) -> bool:
        """Dispatch an Action. screen_coords maps logical slots → pixel (x, y)."""
        if not self._enabled:
            log.info(f"[dry-run] {action.kind} :: {action.reason}")
            return False

        if action.kind == "buy":
            return self._click(screen_coords[f"shop_{action.shop_index}"])
        if action.kind == "sell":
            return self._drag(
                screen_coords[f"bench_{action.bench_index}"],
                screen_coords["sell_zone"],
            )
        if action.kind == "place":
            return self._drag(
                screen_coords[f"bench_{action.bench_index}"]
                if action.bench_index is not None
                else screen_coords[f"board_{action.board_from[0]}_{action.board_from[1]}"],
                screen_coords[f"board_{action.board_to[0]}_{action.board_to[1]}"],
            )
        if action.kind == "reroll":
            return self._press("d")
        if action.kind == "level":
            return self._press("f")
        if action.kind == "lock_shop":
            return self._press("e")

        log.warning(f"Unknown action kind: {action.kind}")
        return False

    # --- primitives ---------------------------------------------------------

    def _sleep_click(self) -> None:
        lo, hi = self.cfg.click_delay_ms
        time.sleep(random.uniform(lo, hi) / 1000)

    def _move_duration(self) -> float:
        lo, hi = self.cfg.move_duration_ms
        return random.uniform(lo, hi) / 1000

    def _click(self, pos: tuple[int, int]) -> bool:
        self._move_to(pos)
        self._sleep_click()
        pydirectinput.click()  # type: ignore
        return True

    def _drag(self, src: tuple[int, int], dst: tuple[int, int]) -> bool:
        self._move_to(src)
        self._sleep_click()
        pydirectinput.mouseDown()  # type: ignore
        self._move_to(dst)
        self._sleep_click()
        pydirectinput.mouseUp()  # type: ignore
        return True

    def _press(self, key: str) -> bool:
        self._sleep_click()
        pydirectinput.press(key)  # type: ignore
        return True

    def _move_to(self, pos: tuple[int, int]) -> None:
        """Move with optional bezier jitter; falls back to linear if disabled."""
        duration = self._move_duration()
        if not self.cfg.bezier_jitter:
            pydirectinput.moveTo(pos[0], pos[1], duration=duration)  # type: ignore
            return

        current = pydirectinput.position()  # type: ignore
        steps = max(8, int(duration * 60))
        ctrl_x = (current[0] + pos[0]) / 2 + random.randint(-80, 80)
        ctrl_y = (current[1] + pos[1]) / 2 + random.randint(-80, 80)
        for i in range(1, steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * current[0] + 2 * (1 - t) * t * ctrl_x + t * t * pos[0]
            y = (1 - t) ** 2 * current[1] + 2 * (1 - t) * t * ctrl_y + t * t * pos[1]
            pydirectinput.moveTo(int(x), int(y))  # type: ignore
            time.sleep(duration / steps)
