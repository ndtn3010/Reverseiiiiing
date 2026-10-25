"""CV detection: UI regions, template matching for champion portraits.

Strategy:
  1. Static UI regions (anchored to resolution) → crop sub-images.
  2. OCR for numbers (gold, HP, level, XP, timer) via tesseract OR
     digit-template matching (faster, no extra install).
  3. Template matching for shop champion portraits (cv2.matchTemplate).
  4. Opponent panel: crop right sidebar, read HP + level per row.

Coordinates below are for 1920×1080 and auto-scale to other resolutions
by linear ratio. For 2560×1440 or 3840×2160 the ratios hold.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


def _locate_tesseract() -> str | None:
    """Find bundled or system tesseract.exe."""
    bundled = Path(getattr(sys, "_MEIPASS", ".")) / "tesseract" / "tesseract.exe"
    if bundled.exists():
        return str(bundled)
    exe_dir = Path(sys.argv[0]).resolve().parent / "tesseract" / "tesseract.exe"
    if exe_dir.exists():
        return str(exe_dir)
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if os.path.exists(candidate):
            return candidate
    return None


_TESS_PATH = _locate_tesseract()
if _TESS_PATH:
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = _TESS_PATH
    except ImportError:
        pass

from reverseiiiiing.capture.screen import Region
from reverseiiiiing.state.models import (
    BenchSlot, BoardCell, Champion, GameState, Opponent, Phase, ShopSlot,
)
from reverseiiiiing.utils.logger import get_logger

log = get_logger(__name__)


# ─── UI anchor rectangles @ 1920×1080 ─────────────────────────────────────
# All coordinates: (x, y, w, h) in pixels. Scale uniformly for other res.
ANCHORS_1080 = {
    # Bottom status bar
    "level":         (218, 955, 70, 40),      # "Lvl. 7"
    "xp":            (295, 955, 90, 25),      # "25/56"
    "gold":          (935, 970, 80, 40),      # just the number
    "streak":        (1070, 970, 60, 35),     # fire/water + number
    "stage_round":   (895, 10,  100, 25),     # top center "4-6"
    "timer":         (1110, 10, 60, 30),      # top center "17"

    # Reroll/XP buttons
    "buy_xp":        (175, 1005, 180, 55),
    "reroll":        (175, 1065, 180, 55),

    # Shop slots (5)
    "shop_0":        (420, 965, 170, 115),
    "shop_1":        (593, 965, 170, 115),
    "shop_2":        (768, 965, 170, 115),
    "shop_3":        (1050, 965, 170, 115),   # account for center gold
    "shop_4":        (1230, 965, 170, 115),

    # Bench (9 slots at bottom)
    "bench_0":       (430, 790, 100, 100),
    "bench_8":       (1470, 790, 100, 100),   # last; others interpolated

    # Player HP (right sidebar, "my" row has larger icon)
    "my_hp":         (1870, 410, 60, 40),

    # Opponent sidebar rows (7 entries, right side)
    "opp_row_h":     90,                       # vertical stride between opponents
    "opp_sidebar":   (1770, 190, 150, 850),    # outer bounds of 7 opp rows

    # Trait panel (left sidebar) — one row per active trait
    "trait_panel":   (0, 280, 220, 500),
}


@dataclass
class DetectorConfig:
    template_dir: Path
    champ_match_threshold: float = 0.82
    item_match_threshold: float = 0.85
    base_resolution: tuple[int, int] = (1920, 1080)


class VisionDetector:
    def __init__(self, cfg: DetectorConfig, actual_resolution: tuple[int, int]):
        self.cfg = cfg
        self.actual = actual_resolution
        self._scale_x = actual_resolution[0] / cfg.base_resolution[0]
        self._scale_y = actual_resolution[1] / cfg.base_resolution[1]
        self._templates: dict[str, np.ndarray] = {}
        self._load_templates()

    # ── public ──────────────────────────────────────────────────────────

    def read_state(self, frame: np.ndarray, state: GameState) -> GameState:
        """Fill as much of GameState as we can from a single frame."""
        state.phase = self._detect_phase(frame)
        state.gold = self._read_number(frame, "gold")
        state.level = self._read_number(frame, "level")
        state.hp = self._read_number(frame, "my_hp")
        state.stage = self._read_stage(frame)
        state.shop = self._read_shop(frame)
        state.opponents = self._read_opponents(frame)
        return state

    # ── primitives ──────────────────────────────────────────────────────

    def _scale(self, box: tuple[int, int, int, int]) -> Region:
        x, y, w, h = box
        return Region(
            x=int(x * self._scale_x),
            y=int(y * self._scale_y),
            w=int(w * self._scale_x),
            h=int(h * self._scale_y),
        )

    def _crop(self, frame: np.ndarray, name: str) -> np.ndarray:
        r = self._scale(ANCHORS_1080[name])
        return frame[r.y : r.y + r.h, r.x : r.x + r.w]

    def _load_templates(self) -> None:
        if not self.cfg.template_dir.exists():
            log.warning(f"Template dir missing: {self.cfg.template_dir}")
            return
        for p in self.cfg.template_dir.glob("champs/*.png"):
            img = cv2.imread(str(p), cv2.IMREAD_COLOR)
            if img is not None:
                self._templates[p.stem] = img
        log.info(f"Loaded {len(self._templates)} champion templates")

    # ── readers ─────────────────────────────────────────────────────────

    def _detect_phase(self, frame: np.ndarray) -> Phase:
        """Heuristic: look for 'Buy XP' button color — present in planning only."""
        buy_xp = self._crop(frame, "buy_xp")
        # Simple brightness check — planning phase shows button clearly.
        mean = buy_xp.mean()
        if mean > 60:
            return Phase.PLANNING
        return Phase.COMBAT

    def _read_number(self, frame: np.ndarray, anchor: str) -> int:
        """Extract integer from a region. Uses OCR if available, else returns 0."""
        crop = self._crop(frame, anchor)
        try:
            import pytesseract
            text = pytesseract.image_to_string(
                crop, config="--psm 7 -c tessedit_char_whitelist=0123456789"
            ).strip()
            return int(text) if text.isdigit() else 0
        except (ImportError, ValueError):
            return 0

    def _read_stage(self, frame: np.ndarray) -> str:
        crop = self._crop(frame, "stage_round")
        try:
            import pytesseract
            text = pytesseract.image_to_string(
                crop, config="--psm 7 -c tessedit_char_whitelist=0123456789-"
            ).strip()
            return text or "?-?"
        except ImportError:
            return "?-?"

    def _read_shop(self, frame: np.ndarray) -> list[ShopSlot]:
        slots: list[ShopSlot] = []
        for i in range(5):
            crop = self._crop(frame, f"shop_{i}")
            champ = self._match_champion(crop)
            slots.append(ShopSlot(index=i, champion=champ))
        return slots

    def _match_champion(self, crop: np.ndarray) -> Optional[Champion]:
        """Template-match crop against known champion portraits."""
        if not self._templates or crop.size == 0:
            return None
        best_name, best_score = None, 0.0
        for name, tpl in self._templates.items():
            if tpl.shape[0] > crop.shape[0] or tpl.shape[1] > crop.shape[1]:
                continue
            res = cv2.matchTemplate(crop, tpl, cv2.TM_CCOEFF_NORMED)
            _, score, _, _ = cv2.minMaxLoc(res)
            if score > best_score:
                best_score, best_name = score, name
        if best_score >= self.cfg.champ_match_threshold and best_name:
            # TODO: look up cost/traits from tft-oracle data
            return Champion(api_name=best_name, display_name=best_name, cost=0)
        return None

    def _read_opponents(self, frame: np.ndarray) -> list[Opponent]:
        opponents: list[Opponent] = []
        bar = self._scale(ANCHORS_1080["opp_sidebar"])
        stride = int(ANCHORS_1080["opp_row_h"] * self._scale_y)
        for i in range(7):
            y0 = bar.y + i * stride
            row = frame[y0 : y0 + stride, bar.x : bar.x + bar.w]
            # TODO: OCR per row for name/HP/level
            opponents.append(Opponent(name=f"opp_{i}", hp=0, level=0))
        return opponents
