"""Shared game state models. Every module speaks these dataclasses."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Phase(str, Enum):
    CAROUSEL = "carousel"
    PVE = "pve"
    AUGMENT = "augment"
    PLANNING = "planning"
    COMBAT = "combat"
    UNKNOWN = "unknown"


class Champion(BaseModel):
    api_name: str              # e.g. "TFT14_Jinx"
    display_name: str
    cost: int                  # 1..5
    traits: list[str] = []
    star: int = 1              # 1 | 2 | 3
    items: list[str] = []      # api_names of equipped items


class ShopSlot(BaseModel):
    index: int                 # 0..4
    champion: Optional[Champion] = None  # None = empty / already bought
    locked: bool = False


class BoardCell(BaseModel):
    row: int                   # 0..3 (0 = front)
    col: int                   # 0..6
    champion: Optional[Champion] = None


class BenchSlot(BaseModel):
    index: int                 # 0..8
    champion: Optional[Champion] = None


class Opponent(BaseModel):
    name: str
    hp: int
    level: int
    traits: list[tuple[str, int]] = []   # [(trait, active_count), ...]
    last_seen_board: list[BoardCell] = []


class Augment(BaseModel):
    api_name: str
    display_name: str
    tier: str                            # silver | gold | prismatic


class GameState(BaseModel):
    # Core econ / lifecycle
    phase: Phase = Phase.UNKNOWN
    stage: str = "?-?"                   # e.g. "3-2"
    round_number: int = 0
    gold: int = 0
    level: int = 1
    xp: int = 0
    xp_to_next: int = 0
    hp: int = 100
    win_streak: int = 0
    loss_streak: int = 0

    # Player state
    shop: list[ShopSlot] = Field(default_factory=list)
    bench: list[BenchSlot] = Field(default_factory=list)
    board: list[BoardCell] = Field(default_factory=list)
    augments: list[Augment] = Field(default_factory=list)
    bench_items: list[str] = Field(default_factory=list)   # unequipped components / full items

    # Lobby
    opponents: list[Opponent] = Field(default_factory=list)

    # Meta hints (filled in by decision engine, not reader)
    target_comp: Optional[str] = None
    target_level_this_stage: Optional[int] = None

    def active_traits(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for cell in self.board:
            if cell.champion is None:
                continue
            for t in cell.champion.traits:
                counts[t] = counts.get(t, 0) + 1
        return counts


class Action(BaseModel):
    kind: str                     # buy | sell | place | reroll | level | use_item | lock_shop
    priority: int                 # 0 highest
    reason: str
    # Params depend on kind:
    shop_index: Optional[int] = None
    bench_index: Optional[int] = None
    board_from: Optional[tuple[int, int]] = None
    board_to: Optional[tuple[int, int]] = None
    item_name: Optional[str] = None
