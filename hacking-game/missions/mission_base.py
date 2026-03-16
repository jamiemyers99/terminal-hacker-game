"""
mission_base.py — Base class for all missions.

Each mission inherits from MissionBase and overrides the class attributes
and run() method to define its narrative, difficulty, rewards, and the
systems/mini-games it chains together.
"""

from __future__ import annotations

from engine.display import colour_print, slow_print, clear_screen
from engine.player import Player


class MissionBase:
    """Base class for a game mission.

    Class attributes to override in subclasses
    ------------------------------------------
    mission_id        : Unique string key used in the save file.
    title             : Human-readable mission name.
    difficulty        : Star rating 1–5 shown in the mission header.
    narrative_intro   : Text shown when the mission starts.
    narrative_success : Text shown on a successful run.
    narrative_failure : Text shown when the player is caught.
    reward_credits    : Credits added to the player on completion.
    reward_tools      : Tools unlocked on completion (permanent).
    """

    mission_id:        str  = "base"
    title:             str  = "UNKNOWN MISSION"
    difficulty:        int  = 1
    narrative_intro:   str  = "You have a new mission. Good luck."
    narrative_success: str  = "Mission complete. Uplink terminated."
    narrative_failure: str  = "Mission failed. Cover blown."
    reward_credits:    int  = 0
    reward_tools:      list = []

    def __init__(self, player: Player) -> None:
        self.player:    Player = player
        self.completed: bool   = False
        self.failed:    bool   = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Display the mission briefing header and introductory narrative."""
        clear_screen()
        print()
        colour_print('  ╔═ INCOMING TRANSMISSION ══════════════════════════╗', 'cyan')
        colour_print(f'  ║  MISSION  : {self.title.upper():<38}║', 'cyan')
        colour_print(f'  ║  THREAT   : {"★" * self.difficulty:<38}║', 'cyan')
        colour_print('  ╚══════════════════════════════════════════════════╝', 'cyan')
        print()
        slow_print(self.narrative_intro, delay=0.03, colour='green')
        print()

    def complete(self) -> None:
        """Mark the mission complete, award all rewards, and reset trace.

        Idempotent — safe to call more than once; subsequent calls no-op.
        """
        if self.completed:
            return
        self.completed = True
        print()
        slow_print(self.narrative_success, delay=0.03, colour='green')
        if self.reward_credits:
            self.player.credits += self.reward_credits
            colour_print(f'\n  [+] Reward: {self.reward_credits} credits deposited.', 'yellow')
        for tool in self.reward_tools:
            if self.player.add_tool(tool):
                colour_print(f'  [+] Tool unlocked: {tool}', 'cyan')
        # Clean disconnect — wipe trace so each mission starts fresh
        self.player.reset_trace()

    def fail(self) -> None:
        """Mark the mission as failed.

        Idempotent — safe to call more than once; subsequent calls no-op.
        """
        if self.failed:
            return
        self.failed = True
        print()
        slow_print(self.narrative_failure, delay=0.03, colour='red')

    # ── Subclass interface ────────────────────────────────────────────────────

    def run(self) -> bool:
        """Execute the mission's gameplay logic.

        Returns True on success, False on failure.
        Must be overridden in every concrete subclass.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run()"
        )
