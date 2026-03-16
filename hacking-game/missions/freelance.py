"""
freelance.py — Procedurally generated freelance contract mission.

Randomly assembles a unique briefing from fragment pools and routes the
player into a system that matches the chosen difficulty tier.

Difficulty tiers
----------------
  1  Low-sec   : CorporateServer  — Password Cracker  (easy)
  2  Mid-sec   : BankNetwork      — Sequence Decoder   (medium)
  3  High-sec  : MilitaryFirewall — Firewall Maze       (hard)

Each FreelanceMission instance generates a distinct target, client,
and objective so no two runs feel the same.
"""

import random
from typing import Tuple

from engine.player         import Player
from engine.utils          import pause
from missions.mission_base import MissionBase


# ---------------------------------------------------------------------------
# Narrative fragment pools
# ---------------------------------------------------------------------------

_CLIENTS = [
    "An anonymous darknet contact",
    "A whistleblower organisation operating through an encrypted relay",
    "A rival corporation acting through a shell company",
    "An investigative journalist — source unverified",
    "A private intelligence broker",
    "A former insider with unfinished business",
    "An unknown party — funds verified, identity redacted",
    "A union representative protecting their members",
    "A foreign press consortium with deep pockets",
    "A city councillor with something to prove",
]

_TARGETS: list = [
    ("OmniTech Industries",   "internal data archive"),
    ("Meridian Analytics",    "research repository"),
    ("Vortex Capital",        "transaction ledger"),
    ("Aegis Security Corp",   "personnel database"),
    ("Strix Communications",  "internal comms server"),
    ("Helion Biomedical",     "clinical trials registry"),
    ("Paragon Logistics",     "shipment routing system"),
    ("Crucible Dynamics",     "R&D prototype database"),
    ("Halcyon Insurance",     "claims processing archive"),
    ("Zenith Media Group",    "content moderation logs"),
    ("Axiom Pharmaceuticals", "drug approval documentation"),
    ("Crestline Energy",      "grid management system"),
]

_OBJECTIVES = [
    "extract personnel files before a scheduled system purge",
    "retrieve encrypted financial records for an ongoing investigation",
    "pull communications logs implicating a senior executive",
    "copy proprietary research data before it is transferred off-site",
    "access a client roster that someone powerful wants buried",
    "recover a deleted document from an offsite backup partition",
    "exfiltrate an internal risk assessment that was never made public",
    "obtain authentication credentials for an external relay node",
    "pull a suppressed audit report from the compliance archive",
    "retrieve a contract that was quietly amended without consent",
]

_COMPLICATIONS = [
    "The target upgraded their intrusion detection last week.",
    "Intel suggests an internal leak — someone may be watching.",
    "Their last attempted breach was logged. They are paranoid now.",
    "The maintenance window is narrow. Move fast.",
    "Their admin runs irregular trace sweeps. Do not linger.",
    "A routine external audit is running in parallel. Tread carefully.",
    "Three other operators turned this job down. Draw your own conclusions.",
    "",   # clean job
    "",   # weight toward no complication
    "",   # weight toward no complication
]


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def _assemble_briefing(target_name: str, target_type: str) -> str:
    client = random.choice(_CLIENTS)
    obj    = random.choice(_OBJECTIVES)
    comp   = random.choice(_COMPLICATIONS)

    text = (
        f"{client} has hired you to {obj}\n"
        f"  from {target_name}'s {target_type}."
    )
    if comp:
        text += f"\n\n  {comp}"
    return text


def _pick_system_class(difficulty: int):
    from systems.corporate_server  import CorporateServer
    from systems.bank_network      import BankNetwork
    from systems.military_firewall import MilitaryFirewall

    return {
        1: CorporateServer,
        2: BankNetwork,
        3: MilitaryFirewall,
    }.get(difficulty, CorporateServer)


# ---------------------------------------------------------------------------
# FreelanceMission
# ---------------------------------------------------------------------------

class FreelanceMission(MissionBase):
    """A procedurally generated one-off contract with randomised narrative."""

    mission_id     = 'freelance'
    title          = 'FREELANCE CONTRACT'
    reward_credits = 0   # credits come from system.on_success(), not the mission
    reward_tools   : list = []

    def __init__(self, player: Player, difficulty: int = 1) -> None:
        super().__init__(player)
        self.difficulty = difficulty

        target_name, target_type = random.choice(_TARGETS)
        self.title           = target_name.upper()
        self.narrative_intro = _assemble_briefing(target_name, target_type)
        self.narrative_success = (
            "Data extracted.  Uplink terminated cleanly.\n"
            "  Payment confirmed.  No trace.  Another ghost job, done right."
        )
        self.narrative_failure = (
            "Connection severed.  You pulled out before full lockout,\n"
            "  but the data is still in there.  The client won't be pleased."
        )

        self._system = _pick_system_class(difficulty)(player)

    def run(self) -> bool:
        """Reset trace, enter the system, and handle outcome."""
        self.player.reset_trace()
        result = self._system.enter(difficulty=self.difficulty)

        if result:
            self.complete()
        else:
            self.fail()

        return result
