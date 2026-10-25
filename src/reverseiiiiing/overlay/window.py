"""PyQt6 transparent always-on-top overlay.

Shows:
  - Current recommended action (big text)
  - Secondary actions (list)
  - Live state: stage, gold, HP, level
  - Mode indicator (COACH / SEMI / FULL)
  - Hotkey hints
"""
from __future__ import annotations

from typing import Optional

try:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QColor, QFont, QPalette
    from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    QApplication = None  # type: ignore

from reverseiiiiing.state.models import Action, GameState


class OverlayWindow(QWidget):
    def __init__(self, mode: str = "COACH_ONLY"):
        super().__init__()
        self.mode = mode
        self._state: Optional[GameState] = None
        self._actions: list[Action] = []
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(340, 240)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 15, 220))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        self.header = QLabel(f"Reverseiii · {self.mode}")
        self.header.setStyleSheet("color: #8aa; font-size: 11px;")

        self.state_line = QLabel("Waiting for game…")
        self.state_line.setStyleSheet("color: #ddd; font-size: 12px;")

        self.action_main = QLabel("")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        self.action_main.setFont(f)
        self.action_main.setStyleSheet("color: #7fc; margin-top: 6px;")
        self.action_main.setWordWrap(True)

        self.action_secondary = QLabel("")
        self.action_secondary.setStyleSheet("color: #aaa; font-size: 11px;")
        self.action_secondary.setWordWrap(True)

        self.hotkeys = QLabel("F8 hide · F9 execute · ESC panic")
        self.hotkeys.setStyleSheet("color: #556; font-size: 10px; margin-top: 6px;")

        for w in (self.header, self.state_line, self.action_main,
                  self.action_secondary, self.hotkeys):
            layout.addWidget(w)
        layout.addStretch()

    def render(self, state: GameState, actions: list[Action]) -> None:
        self._state = state
        self._actions = actions
        self.state_line.setText(
            f"Stage {state.stage}  ·  Lv {state.level}  ·  {state.gold}g  ·  {state.hp}hp"
        )
        if actions:
            top = actions[0]
            self.action_main.setText(f"→ {top.kind.upper()}: {top.reason}")
            secondary = "\n".join(
                f"· {a.kind} — {a.reason}" for a in actions[1:4]
            )
            self.action_secondary.setText(secondary)
        else:
            self.action_main.setText("· idle ·")
            self.action_secondary.setText("")

    def place_top_right(self, screen_w: int) -> None:
        self.move(screen_w - self.width() - 20, 60)


def run_overlay_standalone(mode: str = "COACH_ONLY") -> int:
    if QApplication is None:
        raise RuntimeError("PyQt6 not installed")
    import sys
    app = QApplication(sys.argv)
    win = OverlayWindow(mode)
    win.place_top_right(1920)
    win.show()
    return app.exec()
