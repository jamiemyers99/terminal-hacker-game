"""
ghost_protocol.py — Mission 3: GHOST PROTOCOL

Difficulty  : ★★★
System      : MilitaryFirewall  (Daedalus Defence Network)
Mini-game   : Firewall Maze  (hard — size 3, 9×9)
Reward      : root_kit tool  +  1000 credits

Tool interaction
----------------
vpn_shield  (from Mission 2) — single-use, consumed on mission start:
  Sets player.trace_multiplier = 0.5 for the duration of this mission,
  halving all incoming trace amounts.  Multiplier is reset to 1.0 on
  mission end (success or failure).

root_kit is awarded on success and can be used in Mission 4.
"""

from engine.display        import colour_print, slow_print
from engine.utils          import pause
from missions.mission_base import MissionBase
from systems.military_firewall import MilitaryFirewall


class GhostProtocol(MissionBase):

    mission_id        = "mission_3"
    title             = "GHOST PROTOCOL"
    difficulty        = 3
    reward_credits    = 1000
    reward_tools      : list = ['root_kit']

    narrative_intro = (
        "The money trail ends at Daedalus Defence — a government military\n"
        "  contractor with classified access to the city's entire security grid.\n\n"
        "  Someone high up is using Daedalus as a pass-through.  Your client\n"
        "  needs the command chain — names, ranks, authorisation codes.\n\n"
        "  Daedalus monitors every packet.  One wrong move and you'll be traced\n"
        "  back to your rig before you can pull the plug.\n\n"
        "  Stay ghost."
    )

    narrative_success = (
        "You made it through.  The command chain is in your hands.\n"
        "  Names.  Ranks.  Authorisation trails leading all the way up.\n\n"
        "  On your way out you stripped a root kit from an unpatched server.\n"
        "  One free pass — use it when you need it most."
    )

    narrative_failure = (
        "Daedalus locked you out.  Their automated countermeasures triggered\n"
        "  before you could reach the comms archive.\n"
        "  You're out — but they know someone was in."
    )

    def run(self) -> bool:
        # ── Tool: vpn_shield — halve trace gain ───────────────────────────────
        vpn_active = False
        if self.player.has_tool('vpn_shield'):
            self.player.use_tool('vpn_shield')
            self.player.trace_multiplier = 0.5
            vpn_active = True
            colour_print(
                "\n  [VPN SHIELD]  Routing through encrypted relay nodes...",
                'cyan'
            )
            pause(0.8)
            colour_print(
                "  [VPN SHIELD]  Active.  All trace exposure halved this session.\n",
                'cyan'
            )
            pause(0.5)

        system = MilitaryFirewall(self.player)
        result = system.enter(difficulty=3)

        # ── Always restore multiplier regardless of outcome ───────────────────
        if vpn_active:
            self.player.trace_multiplier = 1.0

        if result:
            self.complete()
        else:
            self.fail()

        return result
