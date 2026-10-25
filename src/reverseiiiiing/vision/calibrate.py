"""Auto-calibration of anchor coords.

The 1920×1080 anchor table in detector.py was hand-measured. For any other
resolution we linearly scale, which works for 2560×1440, 3840×2160 and
most windowed modes — the TFT UI is layout-stable across aspect ratios
within the same horizontal/vertical ratio.

If a user runs ultra-wide (3440×1440) or 4:3, the shop + sidebar move
relative to the border. In that case we re-anchor from landmarks:
  - "Buy XP" button has a distinct yellow icon → template match for its
    corner → derive bottom-bar y offset.
  - Right sidebar first opponent portrait rectangle has fixed color
    border → template match for its top edge → derive sidebar x offset.

Falls back to the pure linear scale if landmarks aren't matched.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from reverseiiiiing.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class CalibrationResult:
    scale_x: float
    scale_y: float
    bottom_bar_y: int | None = None     # if we detected it, overrides scaling
    sidebar_x: int | None = None
    ok: bool = True
    note: str = "linear-scale"


def calibrate(frame: np.ndarray, templates_dir: Path,
              base_res: tuple[int, int] = (1920, 1080)) -> CalibrationResult:
    h, w = frame.shape[:2]
    sx = w / base_res[0]
    sy = h / base_res[1]

    # Try to improve on linear scale via landmark detection
    tried = 0
    bar_y, side_x = None, None
    for name, matcher in (
        ("buy_xp.png",   lambda tpl: _match_bottomleft(frame, tpl)),
        ("sidebar.png",  lambda tpl: _match_righttop(frame, tpl)),
    ):
        p = templates_dir / "ui" / name
        if not p.exists():
            continue
        tpl = cv2.imread(str(p), cv2.IMREAD_COLOR)
        if tpl is None:
            continue
        result = matcher(tpl)
        tried += 1
        if result is not None:
            if name == "buy_xp.png":
                bar_y = result[1]
            else:
                side_x = result[0]

    note = f"linear-scale (sx={sx:.3f} sy={sy:.3f})"
    if bar_y or side_x:
        note = f"landmark-adjusted (bar_y={bar_y}, sidebar_x={side_x})"

    log.info(f"Calibration: {w}x{h} → {note}")
    return CalibrationResult(scale_x=sx, scale_y=sy,
                             bottom_bar_y=bar_y, sidebar_x=side_x, note=note)


def _match_bottomleft(frame: np.ndarray, tpl: np.ndarray) -> tuple[int, int] | None:
    res = cv2.matchTemplate(frame, tpl, cv2.TM_CCOEFF_NORMED)
    _, score, _, loc = cv2.minMaxLoc(res)
    return loc if score > 0.75 else None


def _match_righttop(frame: np.ndarray, tpl: np.ndarray) -> tuple[int, int] | None:
    res = cv2.matchTemplate(frame, tpl, cv2.TM_CCOEFF_NORMED)
    _, score, _, loc = cv2.minMaxLoc(res)
    return loc if score > 0.75 else None
