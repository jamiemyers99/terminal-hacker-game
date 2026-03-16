"""
military_firewall.py — Daedalus Defence Network (security level 3).

Mini-game : Firewall Maze (hard)
Loot      : 1000 credits
"""

from engine.display  import clear_screen, slow_print
from engine.utils    import pause
from systems.base_system import BaseSystem
from minigames.firewall_maze import firewall_maze_minigame
from assets.ascii_art import MILITARY_BANNER


class MilitaryFirewall(BaseSystem):

    name           = "DAEDALUS_DEF"
    security_level = 3
    banner_text    = "DAEDALUS DEFENCE — CLASSIFIED NETWORK"
    loot_credits   = 1000
    loot_tools     : list = []

    flavour_text = (
        "Daedalus Defence. Government-contracted. Heavily monitored.\n"
        "  Every node in this network is a firewall layer — one wrong move and\n"
        "  you'll be traced back to your rig inside sixty seconds.\n"
        "  Find the route through. Leave no footprints."
    )

    def connect(self) -> None:
        clear_screen()
        print(MILITARY_BANNER)
        print()
        slow_print(self.flavour_text, delay=0.025, colour='green')
        print()
        pause(0.5)

    def run_minigame(self, difficulty: int) -> bool:
        return firewall_maze_minigame(difficulty, self.player)
