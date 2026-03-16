"""
base_system.py — Base class for all hackable systems.

Each system in the game (corporate server, bank, military firewall, AI core)
inherits from BaseSystem and overrides class attributes and run_minigame()
to define its unique behaviour and challenge.
"""

from __future__ import annotations

from engine.display import colour_print, slow_print, print_banner, clear_screen
from engine.player  import Player
from engine.sound   import play_sound


class BaseSystem:
    """Base class for a hackable target system.

    Class attributes to override in subclasses
    ------------------------------------------
    name            : Short system identifier used internally.
    security_level  : Difficulty rating 1 (easy) → 5 (extreme).
    banner_text     : Text shown in the connection banner box.
    flavour_text    : Narrative description shown on connect.
    loot_credits    : Credits awarded on a successful hack.
    loot_tools      : List of tool names unlocked on success.
    """

    name:           str  = "UNKNOWN_SYS"
    security_level: int  = 1
    banner_text:    str  = "CONNECTED TO UNKNOWN SYSTEM"
    flavour_text:   str  = "You are connected to an unidentified system."
    loot_credits:   int  = 100
    loot_tools:     list = []

    def __init__(self, player: Player) -> None:
        self.player = player

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Display the connection banner and flavour text."""
        clear_screen()
        print()
        print_banner(self.banner_text)
        print()
        slow_print(self.flavour_text, delay=0.025, colour='green')
        print()

    # ── Outcomes ─────────────────────────────────────────────────────────────

    def on_success(self) -> None:
        """Award loot to the player after a successful intrusion."""
        play_sound('success')
        self.player.credits += self.loot_credits
        colour_print(f'\n  [+] {self.loot_credits} credits transferred to your account.', 'yellow')
        for tool in self.loot_tools:
            if self.player.add_tool(tool):
                colour_print(f'  [+] Tool acquired: {tool}', 'cyan')

    def on_bust(self) -> None:
        """Handle the player being caught by the system's countermeasures."""
        play_sound('bust')
        colour_print('\n  [!] TRACE COMPLETE — INTRUSION DETECTED', 'red')
        colour_print('  [!] Remote countermeasures have flagged your connection.', 'red')
        colour_print('  [!] Neural link terminated by host system.\n', 'red')

    # ── Mini-game interface ───────────────────────────────────────────────────

    def run_minigame(self, difficulty: int) -> bool:
        """Run the system's mini-game challenge.

        Returns True if the player succeeds, False if they are caught.
        Must be overridden in every concrete subclass.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run_minigame(difficulty)"
        )

    # ── Entry point ───────────────────────────────────────────────────────────

    def enter(self, difficulty: int = 1) -> bool:
        """Full connection flow: connect → mini-game → outcome.

        Returns True on success, False if the player is caught.
        """
        self.connect()
        result = self.run_minigame(difficulty)
        if result:
            self.on_success()
        else:
            self.on_bust()
        return result
