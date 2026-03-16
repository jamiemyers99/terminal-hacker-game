"""
bank_network.py — Iron Vault Financial secure gateway (security level 2).

Mini-game : Sequence Decoder (medium)
Loot      : 500 credits
"""

from engine.display  import clear_screen, slow_print
from engine.utils    import pause
from systems.base_system import BaseSystem
from minigames.sequence_decoder import sequence_decoder_minigame
from assets.ascii_art import BANK_BANNER


class BankNetwork(BaseSystem):

    name           = "IRON_VAULT"
    security_level = 2
    banner_text    = "IRON VAULT FINANCIAL — SECURE GATEWAY"
    loot_credits   = 500
    loot_tools     : list = []

    flavour_text = (
        "Iron Vault Financial. One of the most fortified private networks in the city.\n"
        "  Their transaction logs are encrypted behind a rotating cipher sequence.\n"
        "  Decode the sequence and you'll have everything your client needs.\n"
        "  The clock is ticking — their monitoring systems are always on."
    )

    def connect(self) -> None:
        clear_screen()
        print(BANK_BANNER)
        print()
        slow_print(self.flavour_text, delay=0.025, colour='green')
        print()
        pause(0.5)

    def run_minigame(self, difficulty: int) -> bool:
        return sequence_decoder_minigame(difficulty, self.player)
