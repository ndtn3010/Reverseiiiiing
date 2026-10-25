"""YAML config loader with local override."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path = "config/config.yaml") -> dict[str, Any]:
    path = Path(path)
    base = yaml.safe_load(path.read_text(encoding="utf-8"))

    local = path.with_name(path.stem + ".local" + path.suffix)
    if local.exists():
        _deep_merge(base, yaml.safe_load(local.read_text(encoding="utf-8")) or {})

    return base


def _deep_merge(dst: dict, src: dict) -> dict:
    for k, v in src.items():
        if k in dst and isinstance(dst[k], dict) and isinstance(v, dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst
