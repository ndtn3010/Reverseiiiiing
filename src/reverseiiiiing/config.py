from pathlib import Path

import yaml
from pydantic import BaseModel


class DBConfig(BaseModel):
    path: str


class CDragonConfig(BaseModel):
    base_url: str
    tft_json_path: str
    content_metadata: str
    timeout_sec: int = 30


class DDragonConfig(BaseModel):
    versions_url: str


class SetConfig(BaseModel):
    current: int
    rollover_date: str
    next: int


class RefreshConfig(BaseModel):
    cdragon_cron: str
    patch_watcher_cron: str
    meta_comps_cron: str


class HTTPConfig(BaseModel):
    user_agent: str


class Config(BaseModel):
    db: DBConfig
    cdragon: CDragonConfig
    ddragon: DDragonConfig
    set: SetConfig
    refresh: RefreshConfig
    http: HTTPConfig


def load_config(path: str | Path = "config.yaml") -> Config:
    with open(path) as f:
        return Config.model_validate(yaml.safe_load(f))
