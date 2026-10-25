"""First-run wizard + edit settings dialog.

Writes `config/local.yaml`, which overrides the shipped `config/config.yaml`.
If local.yaml is missing (or key fields blank), main.py opens this on
startup and blocks until the user clicks Save.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QIcon
    from PyQt6.QtWidgets import (
        QApplication, QCheckBox, QComboBox, QDialog, QFormLayout, QGroupBox,
        QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTabWidget,
        QVBoxLayout, QWidget,
    )
except ImportError:  # pragma: no cover
    QDialog = object  # type: ignore


REGIONS = ["vn2", "sea", "kr", "jp1", "euw1", "eun1", "na1", "br1", "oc1",
           "tr1", "ru", "la1", "la2"]


@dataclass
class UserSettings:
    riot_api_key: str = ""
    summoner_name: str = ""
    tag_line: str = ""
    region: str = "vn2"
    mode: str = "COACH_ONLY"
    hotkey_toggle: str = "f8"
    hotkey_execute: str = "f9"
    hotkey_panic: str = "esc"
    anonymous_telemetry: bool = False

    @classmethod
    def from_config(cls, cfg: dict) -> "UserSettings":
        u = cfg.get("user", {}) or {}
        exec_cfg = cfg.get("executor", {}) or {}
        return cls(
            riot_api_key=u.get("riot_api_key", ""),
            summoner_name=u.get("summoner_name", ""),
            tag_line=u.get("tag_line", ""),
            region=u.get("region", "vn2"),
            mode=cfg.get("mode", "COACH_ONLY"),
            hotkey_toggle=exec_cfg.get("hotkey_toggle", "f8"),
            hotkey_execute=exec_cfg.get("hotkey_execute", "f9"),
            hotkey_panic=exec_cfg.get("hotkey_panic", "esc"),
        )

    def to_overlay_dict(self) -> dict:
        return {
            "mode": self.mode,
            "user": {
                "riot_api_key": self.riot_api_key,
                "summoner_name": self.summoner_name,
                "tag_line": self.tag_line,
                "region": self.region,
            },
            "executor": {
                "hotkey_toggle": self.hotkey_toggle,
                "hotkey_execute": self.hotkey_execute,
                "hotkey_panic": self.hotkey_panic,
            },
        }

    def is_complete(self) -> bool:
        return bool(self.summoner_name and self.tag_line and self.region)


def write_local_yaml(path: Path, settings: UserSettings) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if path.exists():
        existing = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    _deep_merge(existing, settings.to_overlay_dict())
    path.write_text(
        yaml.safe_dump(existing, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _deep_merge(dst: dict, src: dict) -> dict:
    for k, v in src.items():
        if k in dst and isinstance(dst[k], dict) and isinstance(v, dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


# ─────────────────────────── UI ──────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, settings: UserSettings, parent: Optional[QWidget] = None,
                 first_run: bool = False):
        super().__init__(parent)
        self.settings = settings
        self.first_run = first_run

        self.setWindowTitle("Reverseiii — Settings" if not first_run
                            else "Reverseiii — First-run setup")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._apply_dark_theme()
        self._build()

    def _apply_dark_theme(self) -> None:
        self.setStyleSheet("""
            QDialog, QWidget { background-color: #15161c; color: #ddd; }
            QGroupBox {
                border: 1px solid #333; border-radius: 6px;
                margin-top: 10px; padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QLineEdit, QComboBox {
                background: #0d0e13; color: #eee; border: 1px solid #333;
                border-radius: 4px; padding: 5px 7px;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #4b7; }
            QPushButton {
                background: #263; color: #fff; border: 0; border-radius: 4px;
                padding: 7px 16px; font-weight: 600;
            }
            QPushButton:hover { background: #385; }
            QPushButton#secondary { background: #333; }
            QPushButton#secondary:hover { background: #444; }
            QLabel#hint { color: #889; font-size: 11px; }
            QLabel#risk { color: #e97; font-size: 11px; }
            QTabBar::tab {
                background: #1b1c22; padding: 7px 14px;
                border-top-left-radius: 4px; border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { background: #263; }
        """)

    def _build(self) -> None:
        root = QVBoxLayout(self)

        header = QLabel("Welcome. Fill in your Riot details below."
                        if self.first_run else "Edit your settings.")
        header.setStyleSheet("font-size: 13px; color: #bbb; padding-bottom: 6px;")
        root.addWidget(header)

        tabs = QTabWidget()
        tabs.addTab(self._tab_account(),  "Account")
        tabs.addTab(self._tab_mode(),     "Mode")
        tabs.addTab(self._tab_hotkeys(),  "Hotkeys")
        root.addWidget(tabs)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondary")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save")
        save.clicked.connect(self._on_save)
        if self.first_run:
            cancel.setEnabled(False)
            cancel.setToolTip("Required on first run")
        btns.addWidget(cancel)
        btns.addWidget(save)
        root.addLayout(btns)

    def _tab_account(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.e_name = QLineEdit(self.settings.summoner_name)
        self.e_name.setPlaceholderText("e.g. He")
        self.e_tag = QLineEdit(self.settings.tag_line)
        self.e_tag.setPlaceholderText("e.g. VN2")
        self.e_region = QComboBox()
        self.e_region.addItems(REGIONS)
        self.e_region.setCurrentText(self.settings.region)
        self.e_key = QLineEdit(self.settings.riot_api_key)
        self.e_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.e_key.setPlaceholderText("RGAPI-… (optional, enables match history)")

        form.addRow("Summoner name:", self.e_name)
        form.addRow("Tag line:", self.e_tag)
        form.addRow("Region:", self.e_region)
        form.addRow("Riot API key:", self.e_key)

        hint = QLabel("Get a dev key at developer.riotgames.com — expires every "
                      "24h. Leave empty to skip match-history features.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        form.addRow("", hint)
        return w

    def _tab_mode(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)

        self.e_mode = QComboBox()
        self.e_mode.addItems(["COACH_ONLY", "SEMI_AUTO", "FULL_AUTO"])
        self.e_mode.setCurrentText(self.settings.mode)

        v.addWidget(QLabel("Operating mode:"))
        v.addWidget(self.e_mode)

        descriptions = QGroupBox("What each mode does")
        d = QVBoxLayout(descriptions)
        d.addWidget(self._mode_card(
            "COACH_ONLY",
            "Overlay suggests moves. You click. Safest, no input simulation.",
            risk=False,
        ))
        d.addWidget(self._mode_card(
            "SEMI_AUTO",
            "Overlay suggests moves. Press F9 to execute the top action. "
            "Lower risk than full auto because a human triggers each click.",
            risk=False,
        ))
        d.addWidget(self._mode_card(
            "FULL_AUTO",
            "Overlay + the app executes actions on a timer. "
            "Vanguard anti-cheat likely bans accounts using this. "
            "Use only on a disposable account.",
            risk=True,
        ))
        v.addWidget(descriptions)
        v.addStretch()
        return w

    def _mode_card(self, name: str, body: str, risk: bool) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(4, 2, 4, 6)
        title = QLabel(f"<b>{name}</b>")
        label = QLabel(body)
        label.setObjectName("risk" if risk else "hint")
        label.setWordWrap(True)
        v.addWidget(title)
        v.addWidget(label)
        return w

    def _tab_hotkeys(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.e_h_toggle = QLineEdit(self.settings.hotkey_toggle)
        self.e_h_exec = QLineEdit(self.settings.hotkey_execute)
        self.e_h_panic = QLineEdit(self.settings.hotkey_panic)
        form.addRow("Toggle overlay:", self.e_h_toggle)
        form.addRow("Execute (SEMI):", self.e_h_exec)
        form.addRow("Panic kill:", self.e_h_panic)
        hint = QLabel("Use key names: f1-f12, esc, space, a-z, 0-9.")
        hint.setObjectName("hint")
        form.addRow("", hint)
        return w

    def _on_save(self) -> None:
        self.settings.summoner_name = self.e_name.text().strip()
        self.settings.tag_line = self.e_tag.text().strip().lstrip("#")
        self.settings.region = self.e_region.currentText()
        self.settings.riot_api_key = self.e_key.text().strip()
        self.settings.mode = self.e_mode.currentText()
        self.settings.hotkey_toggle = self.e_h_toggle.text().strip().lower()
        self.settings.hotkey_execute = self.e_h_exec.text().strip().lower()
        self.settings.hotkey_panic = self.e_h_panic.text().strip().lower()

        if not self.settings.is_complete():
            QMessageBox.warning(
                self, "Missing info",
                "Summoner name, tag line, and region are required.",
            )
            return

        if self.settings.mode == "FULL_AUTO":
            resp = QMessageBox.warning(
                self, "Confirm FULL_AUTO",
                "FULL_AUTO automates mouse/keyboard input. Vanguard anti-cheat "
                "is very likely to ban accounts that use this. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if resp != QMessageBox.StandardButton.Yes:
                return

        self.accept()


def run_first_run_wizard(local_path: Path, current_cfg: dict) -> UserSettings | None:
    """Show the dialog modally. Returns the saved settings or None if cancelled."""
    app = QApplication.instance() or QApplication([])
    settings = UserSettings.from_config(current_cfg)
    dlg = SettingsDialog(settings, first_run=not settings.is_complete())
    if dlg.exec() == QDialog.DialogCode.Accepted:
        write_local_yaml(local_path, dlg.settings)
        return dlg.settings
    return None
