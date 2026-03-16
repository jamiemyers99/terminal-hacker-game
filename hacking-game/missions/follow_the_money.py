"""
follow_the_money.py — Mission 2: FOLLOW THE MONEY

Difficulty  : ★★
System      : BankNetwork  (Iron Vault Financial)
Mini-game   : Sequence Decoder  (medium)
Reward      : vpn_shield tool  +  500 credits

Tool interaction
----------------
port_scanner  (from Mission 1) — passive advantage:
  If the player carries a port_scanner, it maps an open service port before
  connection, granting a -15 trace buffer (trace_exposure reduced by 15).
  The tool is NOT consumed; it remains in inventory.

vpn_shield is awarded on success and activates in Mission 3.
"""

from engine.display      import colour_print
from engine.utils        import pause, press_enter
from missions.mission_base import MissionBase
from systems.bank_network  import BankNetwork


class FollowTheMoney(MissionBase):

    mission_id        = "mission_2"
    title             = "FOLLOW THE MONEY"
    difficulty        = 2
    reward_credits    = 500
    reward_tools      : list = ['vpn_shield']

    narrative_intro = (
        "The PROJECT LAZARUS files contained more than anyone expected.\n"
        "  Buried in the metadata: routing codes from Iron Vault Financial —\n"
        "  hundreds of millions moving through offshore shells.\n\n"
        "  Your client wants the transaction logs.  Proof the money exists.\n"
        "  Iron Vault uses a rotating cipher sequence on their internal archive.\n\n"
        "  Break the sequence.  Pull the logs.  Follow the money."
    )

    narrative_success = (
        "Transaction logs extracted.  The money trail is real — and it leads\n"
        "  somewhere much darker than a corporate fraud case.\n\n"
        "  Iron Vault's monitoring flagged unusual traffic, but you were already\n"
        "  gone.  Your client has wired a VPN shield to your drop address."
    )

    narrative_failure = (
        "The sequence didn't hold.  Iron Vault's monitoring system isolated\n"
        "  the connection and you had to pull out.\n"
        "  The logs are still in there."
    )

    def run(self) -> bool:
        # ── Tool: port_scanner — trace buffer ─────────────────────────────────
        if self.player.has_tool('port_scanner'):
            colour_print(
                "\n  [PORT SCANNER]  Mapping open service endpoints...",
                'cyan'
            )
            pause(0.8)
            colour_print(
                "  [PORT SCANNER]  Backdoor admin port located.  "
                "Trace buffer granted  (-15).\n",
                'cyan'
            )
            self.player.trace_exposure = max(0, self.player.trace_exposure - 15)
            pause(0.5)

        system = BankNetwork(self.player)
        result = system.enter(difficulty=2)

        if result:
            self.complete()
        else:
            self.fail()

        return result
