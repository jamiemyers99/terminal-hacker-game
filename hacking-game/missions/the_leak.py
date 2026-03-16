"""
the_leak.py — Mission 1: THE LEAK  (Tutorial)

Difficulty  : ★
System      : CorporateServer  (NexusCorp internal network)
Mini-game   : Password Cracker  (easy)
Reward      : port_scanner tool  +  250 credits

Tutorial role
-------------
This mission introduces the core game loop:
  • The trace meter and what it means to be caught
  • How the password cracker works
  • That tools carry forward to future missions

Trace is reset before the mini-game begins so the player has a clean slate
during their first attempt.
"""

from engine.display      import colour_print, slow_print, clear_screen, print_trace_bar
from engine.utils        import pause, press_enter
from missions.mission_base import MissionBase
from systems.corporate_server import CorporateServer


class TheLeak(MissionBase):

    mission_id        = "mission_1"
    title             = "THE LEAK"
    difficulty        = 1
    reward_credits    = 250
    reward_tools      : list = ['port_scanner']

    narrative_intro = (
        "An encrypted message arrived this morning through a dead-drop relay.\n"
        "  The sender: a whistleblower inside NexusCorp — one of the city's\n"
        "  largest tech conglomerates.\n\n"
        "  They need a file pulled from the internal server before it's purged.\n"
        "  The file is called PROJECT LAZARUS.  No questions asked.\n\n"
        "  Low security.  Clean work.  Easy money.\n"
        "  Your first real job."
    )

    narrative_success = (
        "PROJECT LAZARUS extracted.  File delivered to the dead-drop.\n"
        "  Payment confirmed.  Clean disconnect.\n\n"
        "  You found something in the file metadata: a port scanner left on the\n"
        "  server by an old sysadmin.  You've added it to your toolkit."
    )

    narrative_failure = (
        "The connection dropped.  NexusCorp's logging system flagged the attempt.\n"
        "  You got out before they traced you back — but the file is still in there."
    )

    # ── Tutorial tips ─────────────────────────────────────────────────────────

    _TIPS = [
        ("TRACE METER",
         "The TRACE bar fills every time you make a mistake.\n"
         "    Hit 100% and the system locks you out — mission failed."),
        ("PASSWORD CRACKER",
         "Guess the hidden password within the attempt limit.\n"
         "    Wrong guesses cost trace.  Type 'hint' to reveal a letter (costs more trace)."),
        ("TOOLS",
         "Completing missions unlocks tools.  They give you advantages\n"
         "    in future missions.  Keep them safe — some are single-use."),
    ]

    def _show_tutorial(self) -> None:
        clear_screen()
        colour_print("  ╔═ MISSION BRIEFING ════════════════════════════════╗", 'yellow')
        colour_print("  ║  TUTORIAL — Read before connecting                ║", 'yellow')
        colour_print("  ╚══════════════════════════════════════════════════╝\n", 'yellow')

        for title, body in self._TIPS:
            colour_print(f"  ▸  {title}", 'cyan')
            slow_print(f"    {body}\n", delay=0.02, colour='dim')
            pause(0.2)

        press_enter()

    # ── Mission logic ─────────────────────────────────────────────────────────

    def run(self) -> bool:
        self._show_tutorial()

        # Give the tutorial player a clean trace slate
        self.player.reset_trace()
        colour_print("\n  [+] Trace cleared — fresh connection initialised.\n", 'green')
        pause(0.5)

        system = CorporateServer(self.player)
        result = system.enter(difficulty=1)

        if result:
            self.complete()
        else:
            self.fail()

        return result
