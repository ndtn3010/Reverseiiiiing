"""Global hotkey listener (pynput). Thread-safe callbacks."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pynput import keyboard


@dataclass
class HotkeyBinding:
    key: str
    callback: Callable[[], None]


class HotkeyManager:
    def __init__(self):
        self._bindings: dict[str, Callable[[], None]] = {}
        self._listener: keyboard.Listener | None = None

    def bind(self, key: str, callback: Callable[[], None]) -> None:
        self._bindings[key.lower()] = callback

    def start(self) -> None:
        def on_press(k):
            name = self._key_name(k)
            if name and name in self._bindings:
                self._bindings[name]()

        self._listener = keyboard.Listener(on_press=on_press)
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()

    @staticmethod
    def _key_name(k) -> str | None:
        if isinstance(k, keyboard.Key):
            return k.name.lower()
        try:
            return k.char.lower() if k.char else None
        except AttributeError:
            return None
