"""
player.py — Player class and persistent state.

Tracks the player's hacker alias, level, tool inventory, trace exposure,
and credit balance. Includes serialisation helpers for save/load.
"""

from __future__ import annotations
from typing import List


class Player:
    """Represents the player's complete in-game state."""

    MAX_LEVEL: int = 5
    MAX_TRACE: int = 100

    def __init__(self, name: str) -> None:
        self.name:             str        = name
        self.level:            int        = 1
        self.tools:            List[str]  = []
        self.trace_exposure:   int        = 0
        self.credits:          int        = 0
        # Multiplier applied to all incoming trace amounts (vpn_shield sets to 0.5).
        # Reset to 1.0 after the mission that consumed it ends.
        self.trace_multiplier: float      = 1.0

    # ── Tool management ───────────────────────────────────────────────────────

    def add_tool(self, tool: str) -> bool:
        """Add *tool* to inventory. Returns False if already owned."""
        if tool not in self.tools:
            self.tools.append(tool)
            return True
        return False

    def use_tool(self, tool: str) -> bool:
        """Consume a single-use *tool*. Returns False if not in inventory."""
        if tool in self.tools:
            self.tools.remove(tool)
            return True
        return False

    def has_tool(self, tool: str) -> bool:
        """Return True if *tool* is in the player's inventory."""
        return tool in self.tools

    # ── Trace management ──────────────────────────────────────────────────────

    def increase_trace(self, amount: int = 10) -> bool:
        """Increase trace exposure by *amount* (scaled by trace_multiplier).

        Returns True if the player has now been caught (trace reached 100).
        """
        effective = max(1, int(amount * self.trace_multiplier))
        self.trace_exposure = min(self.MAX_TRACE, self.trace_exposure + effective)
        return self.is_caught()

    def reset_trace(self) -> None:
        """Reset trace exposure to zero (e.g. after a clean disconnect)."""
        self.trace_exposure = 0

    def is_caught(self) -> bool:
        """Return True when trace exposure has reached the maximum."""
        return self.trace_exposure >= self.MAX_TRACE

    # ── Progression ───────────────────────────────────────────────────────────

    def level_up(self) -> bool:
        """Increase level by one. Returns False if already at MAX_LEVEL."""
        if self.level < self.MAX_LEVEL:
            self.level += 1
            return True
        return False

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dict of all player state."""
        return {
            'name':           self.name,
            'level':          self.level,
            'tools':          list(self.tools),
            'trace_exposure': self.trace_exposure,
            'credits':        self.credits,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Player:
        """Reconstruct a Player instance from a save-file dict."""
        player                = cls(data['name'])
        player.level          = data.get('level',          1)
        player.tools          = data.get('tools',          [])
        player.trace_exposure = data.get('trace_exposure', 0)
        player.credits        = data.get('credits',        0)
        return player

    def __repr__(self) -> str:
        return (
            f"Player(name={self.name!r}, level={self.level}, "
            f"trace={self.trace_exposure}, credits={self.credits}, "
            f"tools={self.tools})"
        )
