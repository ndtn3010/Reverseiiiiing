"""Rule-based decision engine. Takes GameState → ranked Action list.

Rules are intentionally simple and transparent. They cover:
  - Shop buys that help your target comp or complete a trait threshold
  - Econ: when to roll, when to level, when to hold
  - Level timing (standard TFT breakpoints)
  - Reroll triggers (3-cost reroll at lv7, etc.)

A real meta-driven engine would consult the SQLite meta DB; this v1 uses
heuristics that port across patches.
"""
from __future__ import annotations

from dataclasses import dataclass

from reverseiiiiing.state.models import Action, GameState
from reverseiiiiing.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class EngineConfig:
    comp_match_min_score: float = 0.6
    risk_tolerance: float = 0.5          # 0 = econ max, 1 = aggro


# Standard econ breakpoints (TFT universal)
LEVEL_COST = {4: 4, 5: 8, 6: 20, 7: 36, 8: 48, 9: 76, 10: 100}
INTEREST_CAP = 50     # +1 gold per 10 up to 50


class DecisionEngine:
    def __init__(self, cfg: EngineConfig):
        self.cfg = cfg

    def plan(self, state: GameState) -> list[Action]:
        actions: list[Action] = []

        actions.extend(self._shop_actions(state))
        actions.extend(self._econ_actions(state))
        actions.extend(self._positioning_actions(state))

        actions.sort(key=lambda a: a.priority)
        return actions

    # ── shop ────────────────────────────────────────────────────────────

    def _shop_actions(self, state: GameState) -> list[Action]:
        out: list[Action] = []
        active_traits = state.active_traits()

        for slot in state.shop:
            if slot.champion is None:
                continue
            c = slot.champion
            cost = c.cost or 1
            if state.gold < cost:
                continue

            # Priority: already own 2★ progress > completes trait > just upgrade
            own_count = sum(
                1 for b in state.bench if b.champion and b.champion.api_name == c.api_name
            ) + sum(
                1 for cell in state.board if cell.champion and cell.champion.api_name == c.api_name
            )

            # 3rd copy → 2★ priority 0
            if own_count == 2:
                out.append(Action(
                    kind="buy", priority=0, shop_index=slot.index,
                    reason=f"3rd {c.display_name} → 2★",
                ))
                continue

            # Completes a trait breakpoint
            for trait in c.traits:
                current = active_traits.get(trait, 0)
                # Any trait where we're 1 short of a breakpoint
                if current in {1, 2, 3}:
                    out.append(Action(
                        kind="buy", priority=1, shop_index=slot.index,
                        reason=f"{c.display_name} completes {trait} ({current + 1})",
                    ))
                    break

            # Just a comp unit we want (cheap)
            if cost <= 2 and own_count < 2:
                out.append(Action(
                    kind="buy", priority=3, shop_index=slot.index,
                    reason=f"Cheap {c.display_name} for board",
                ))

        return out

    # ── econ ────────────────────────────────────────────────────────────

    def _econ_actions(self, state: GameState) -> list[Action]:
        out: list[Action] = []

        # Level targets per stage (standard)
        target_level_by_stage = {
            "2-1": 4, "2-5": 5, "3-2": 6, "3-5": 6,
            "4-1": 7, "4-5": 7, "5-1": 8, "6-1": 9,
        }
        target = target_level_by_stage.get(state.stage)

        if target and state.level < target:
            # Buy XP if we can hit target this round
            if state.gold >= 4 + INTEREST_CAP:  # keep interest intact
                out.append(Action(
                    kind="level", priority=2,
                    reason=f"On-tempo level to {target} at {state.stage}",
                ))

        # Reroll triggers:
        # - lv7, 3-cost reroll: if hunting carry at 2★
        # - HP < 30 and streak broken: slam-roll
        if state.hp < 30 and state.gold >= 20:
            out.append(Action(
                kind="reroll", priority=1,
                reason=f"Low HP ({state.hp}), roll down to stabilize",
            ))

        return out

    # ── positioning ─────────────────────────────────────────────────────

    def _positioning_actions(self, state: GameState) -> list[Action]:
        # Placeholder: v2 will suggest row swaps for carry based on
        # opponent assassin/dive threat scan.
        return []
