"""Screen capture via mss + auto resolution detect.

Captures full primary monitor by default; sub-regions passed as (x, y, w, h).
Returns BGR numpy arrays ready for OpenCV.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    import mss
except ImportError:  # pragma: no cover
    mss = None  # type: ignore


@dataclass
class Region:
    x: int
    y: int
    w: int
    h: int

    def as_mss(self) -> dict:
        return {"left": self.x, "top": self.y, "width": self.w, "height": self.h}


def detect_primary_resolution() -> tuple[int, int]:
    """Return (width, height) of the primary monitor. Falls back to 1920×1080."""
    if mss is None:
        return (1920, 1080)
    with mss.mss() as sct:
        mon = sct.monitors[1]
        return (mon["width"], mon["height"])


class ScreenCapture:
    def __init__(self, monitor: int = 1):
        if mss is None:
            raise RuntimeError("mss not installed")
        self._sct = mss.mss()
        self._monitor = monitor

    @property
    def resolution(self) -> tuple[int, int]:
        mon = self._sct.monitors[self._monitor]
        return (mon["width"], mon["height"])

    def grab(self, region: Region | None = None) -> np.ndarray:
        bbox = region.as_mss() if region else self._sct.monitors[self._monitor]
        shot = self._sct.grab(bbox)
        img = np.asarray(shot)[:, :, :3]  # drop alpha, BGR already
        return img

    def close(self) -> None:
        self._sct.close()
