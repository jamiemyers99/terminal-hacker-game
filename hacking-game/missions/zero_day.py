"""
zero_day.py — Mission 4: ZERO DAY  (Final Boss)

Difficulty  : ★★★★★
System      : AICore  (PROMETHEUS city infrastructure)
Mini-games  : All three in sequence — no trace reset between stages
Reward      : 2000 credits  (no tool — this is the end)

Two endings
-----------
After successfully breaching PROMETHEUS, the player makes an irreversible
choice that determines the final narrative:

  [1] GHOST ENDING  — Extract the data and disappear.
      Leak it to the press.  The truth comes out.  You vanish.

  [2] CHAOS ENDING  — Destroy the AI core.
      The city grid collapses.  Traffic, power, comms — all go dark.
      The conspiracy dies.  So does everything it controlled.

Tool interaction
----------------
root_kit  (from Mission 3) — offered per stage inside AICore.run_minigame().
  The player can auto-solve one stage; the tool is consumed on use.
  If not used before Mission 4, it's available here for the first stage
  that feels unbeatable.
"""

from engine.display        import colour_print, slow_print, clear_screen, print_banner
from engine.utils          import safe_input, pause, press_enter
from missions.mission_base import MissionBase
from systems.ai_core       import AICore


class ZeroDay(MissionBase):

    mission_id        = "mission_4"
    title             = "ZERO DAY"
    difficulty        = 5
    reward_credits    = 2000
    reward_tools      : list = []

    narrative_intro = (
        "You've been following this thread for weeks.\n"
        "  A corporate server.  A bank.  A military contractor.\n"
        "  All roads lead here.\n\n"
        "  PROMETHEUS.\n"
        "  The city's AI backbone.  Traffic.  Power.  Comms.  Finance.\n"
        "  Surveillance.  It runs everything — and someone built a back door.\n\n"
        "  PROJECT LAZARUS wasn't a file.  It was a key.\n"
        "  And now you're holding it.\n\n"
        "  This is the zero day.  The one exploit that changes everything.\n"
        "  No second chances.  No retry.  One shot.\n\n"
        "  Make it count."
    )

    narrative_failure = (
        "PROMETHEUS sealed every route the moment you slipped.\n"
        "  You got out — barely.  Your rig is clean, your trace is cold.\n"
        "  But the back door is still there, and so is the conspiracy.\n\n"
        "  The city keeps running.  For now."
    )

    # narrative_success is not used — endings handle their own text

    # ── Ending narratives ─────────────────────────────────────────────────────

    def _ending_ghost(self) -> None:
        clear_screen()
        colour_print("\n  [ ENDING: GHOST ]\n", 'green')
        lines = [
            "You copy everything.  Every file.  Every transaction record.",
            "Every name in the command chain.",
            "",
            "The upload takes eleven seconds.",
            "Fourteen journalists.  Six city oversight bodies.  Three foreign embassies.",
            "",
            "You close the connection.",
            "",
            "By morning it's everywhere.",
            "NexusCorp's board is arrested before the stock market opens.",
            "Daedalus Defence loses its government contracts by noon.",
            "The architects of PROJECT LAZARUS are named.",
            "",
            "You are never mentioned.",
            "You were never there.",
            "",
            "Ghost status: maintained.",
        ]
        for line in lines:
            if line:
                slow_print(f"  {line}", delay=0.03, colour='green')
            else:
                print()
            pause(0.1)

    def _ending_chaos(self) -> None:
        clear_screen()
        colour_print("\n  [ ENDING: CHAOS ]\n", 'red')
        lines = [
            "You find the kill switch.",
            "A single command — hardcoded during PROMETHEUS's original deployment.",
            "Left there by someone who knew this day might come.",
            "",
            "You stare at the cursor for a long time.",
            "",
            "> confirm_shutdown --core --irreversible",
            "",
            "Enter.",
            "",
            "The lights in your window flicker.",
            "Then the city goes dark.",
            "",
            "Traffic signals.  Power grid.  Surveillance network.  Financial routing.",
            "All of it — gone.",
            "",
            "In the silence you hear the city breathing for the first time.",
            "",
            "The conspiracy is dead.",
            "So is everything it built.",
            "",
            "Whether that was the right call —",
            "you'll spend the rest of your life wondering.",
        ]
        for line in lines:
            if line:
                colour = 'red' if line.startswith('>') else 'green'
                slow_print(f"  {line}", delay=0.03, colour=colour)
            else:
                print()
            pause(0.1)

    def _show_ending_choice(self) -> None:
        clear_screen()
        print_banner("PROMETHEUS — BREACHED")
        print()
        slow_print("  You are inside.", delay=0.04, colour='magenta')
        slow_print("  PROMETHEUS is dormant — a sleeping god.", delay=0.04, colour='magenta')
        slow_print("  The entire city breathes through this machine.\n", delay=0.04, colour='magenta')
        pause(0.5)
        slow_print("  You can see everything.  Every secret.  Every name.", delay=0.03, colour='green')
        slow_print("  And you have two choices.\n", delay=0.03, colour='green')
        pause(0.5)

        colour_print("  ╔══════════════════════════════════════════════════════╗", 'cyan')
        colour_print("  ║                                                      ║", 'cyan')
        colour_print("  ║   [1]  Extract the data and disappear                ║", 'green')
        colour_print("  ║        Leak it.  Let the world decide.               ║", 'dim')
        colour_print("  ║                                                      ║", 'cyan')
        colour_print("  ║   [2]  Destroy the core — shut it all down           ║", 'red')
        colour_print("  ║        The conspiracy dies.  So does the city grid.  ║", 'dim')
        colour_print("  ║                                                      ║", 'cyan')
        colour_print("  ╚══════════════════════════════════════════════════════╝\n", 'cyan')

        while True:
            choice = safe_input("\033[96m  > \033[0m").strip()
            if choice == '1':
                self.player.ending = 'ghost'
                self._ending_ghost()
                return
            if choice == '2':
                self.player.ending = 'chaos'
                self._ending_chaos()
                return
            colour_print("  [!] Enter 1 or 2.", 'red')

    # ── Mission logic ─────────────────────────────────────────────────────────

    def run(self) -> bool:
        # Warn player before committing
        colour_print(
            "\n  [!] FINAL MISSION — There is no retry on PROMETHEUS.\n"
            "      Trace does NOT reset between mini-game stages.\n",
            'red'
        )
        press_enter("  [ CONFIRM CONNECTION? ] Press ENTER to proceed...")

        system = AICore(self.player)
        result = system.enter(difficulty=3)

        if not result:
            self.fail()
            return False

        # Success path — award credits then show ending choice
        self.player.credits += self.reward_credits
        colour_print(f"\n  [+] {self.reward_credits} credits transferred.\n", 'yellow')
        pause(0.5)

        self._show_ending_choice()
        press_enter("\n  [ Press ENTER to continue... ]")
        self.completed = True
        return True
