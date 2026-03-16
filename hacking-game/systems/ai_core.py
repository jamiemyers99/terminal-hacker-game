"""
ai_core.py — PROMETHEUS AI Infrastructure Core (security level 5).

Final boss system.  Chains all three mini-games in sequence with NO trace
reset between stages.  If the player owns a root_kit, they are offered the
chance to auto-solve one stage before it begins — the tool is consumed on use.

Mini-games (in order)
---------------------
  Stage 1 : Password Cracker  (difficulty passed through)
  Stage 2 : Sequence Decoder  (difficulty passed through)
  Stage 3 : Firewall Maze     (difficulty passed through)

Loot : 2000 credits
"""

from engine.display  import clear_screen, colour_print, slow_print, print_banner
from engine.utils    import safe_input, pause
from systems.base_system import BaseSystem
from minigames.password_cracker import password_crack_minigame
from minigames.sequence_decoder import sequence_decoder_minigame
from minigames.firewall_maze    import firewall_maze_minigame
from assets.ascii_art import AI_CORE_BANNER


class AICore(BaseSystem):

    name           = "PROMETHEUS_AI"
    security_level = 5
    banner_text    = "PROMETHEUS — CITY INFRASTRUCTURE CORE"
    loot_credits   = 2000
    loot_tools     : list = []

    flavour_text = (
        "PROMETHEUS.\n"
        "  The neural backbone of the entire city — traffic, power, comms,\n"
        "  surveillance, financial routing.  Everything flows through here.\n"
        "  It is aware.  It is watching.  It already knows you're close.\n"
        "  You have one shot.  Don't waste it."
    )

    def connect(self) -> None:
        clear_screen()
        print(AI_CORE_BANNER)
        print()
        slow_print(self.flavour_text, delay=0.03, colour='magenta')
        print()
        pause(1)

    def run_minigame(self, difficulty: int) -> bool:
        """Run all three mini-games in sequence.  No trace reset between stages."""
        stages = [
            ("STAGE 1 / 3  —  PASSWORD CRACKER",
             lambda: password_crack_minigame(difficulty, self.player)),
            ("STAGE 2 / 3  —  SEQUENCE DECODER",
             lambda: sequence_decoder_minigame(difficulty, self.player)),
            ("STAGE 3 / 3  —  FIREWALL BYPASS",
             lambda: firewall_maze_minigame(difficulty, self.player)),
        ]

        for i, (label, game_fn) in enumerate(stages):
            clear_screen()
            colour_print(f"\n  ╔═ {label} {'═' * (42 - len(label))}╗", 'magenta')
            colour_print(  f"  ║  PROMETHEUS countermeasures escalating...          ║", 'magenta')
            colour_print(  f"  ╚{'═' * 52}╝\n", 'magenta')
            pause(0.8)

            # ── Root kit offer ────────────────────────────────────────────────
            if self.player.has_tool('root_kit'):
                colour_print(
                    "  [ROOT KIT DETECTED]  Deploy to auto-solve this stage?  [y/n]",
                    'cyan'
                )
                choice = safe_input("  > ").strip().lower()
                if choice == 'y':
                    self.player.use_tool('root_kit')
                    slow_print(
                        "  > Root kit deployed.  Stage countermeasures neutralised.\n",
                        delay=0.04, colour='cyan'
                    )
                    pause(0.5)
                    continue        # skip this stage

            # ── Run the actual mini-game ───────────────────────────────────────
            if not game_fn():
                slow_print(
                    "\n  > PROMETHEUS ISOLATED YOUR INTRUSION.  LINK SEVERED.\n",
                    delay=0.04, colour='red'
                )
                return False

            slow_print(
                f"\n  > Stage {i + 1} bypassed.  PROMETHEUS destabilised.\n",
                delay=0.04, colour='green'
            )
            pause(0.8)

        return True
