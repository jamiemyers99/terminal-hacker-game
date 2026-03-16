"""
corporate_server.py — NexusCorp Internal Network (security level 1).

Mini-game : Password Cracker (easy)
Loot      : 200 credits
"""

from engine.display  import clear_screen, slow_print
from engine.player   import Player
from engine.utils    import pause
from systems.base_system import BaseSystem
from minigames.password_cracker import password_crack_minigame
from assets.ascii_art import CORPORATE_BANNER


class CorporateServer(BaseSystem):

    name           = "NEXUS_CORP"
    security_level = 1
    banner_text    = "NEXUS CORP — INTERNAL NETWORK"
    loot_credits   = 200
    loot_tools     : list = []

    flavour_text = (
        "You're in. The NexusCorp internal server hums quietly.\n"
        "  Employee records, internal memos, budget reports — all here.\n"
        "  Somewhere in this system is the file your client is paying for.\n"
        "  The admin left a password-protected share. Crack it."
    )

    def connect(self) -> None:
        clear_screen()
        print(CORPORATE_BANNER)
        print()
        slow_print(self.flavour_text, delay=0.025, colour='green')
        print()
        pause(0.5)

    def run_minigame(self, difficulty: int) -> bool:
        return password_crack_minigame(difficulty, self.player)
