"""
career.py — Persistent career stats tracked across all sessions.

Stored in data/career.json.  Updated after every completed story run or
freelance contract.  Displayed from the main menu.

Stat schema
-----------
{
    "story_runs":       int,
    "freelance_runs":   int,
    "lifetime_credits": int,
    "best_run":         int,
    "missions_done":    int,
    "tools_collected":  int,
    "endings": {
        "ghost": int,
        "chaos": int
    }
}
"""

import copy
import json
import os
from typing import Dict

from engine.display import colour_print, clear_screen, print_banner, slow_print
from engine.utils   import pause, press_enter

_GAME_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAREER_PATH = os.path.join(_GAME_ROOT, 'data', 'career.json')

_DEFAULTS: Dict = {
    'story_runs':       0,
    'freelance_runs':   0,
    'lifetime_credits': 0,
    'best_run':         0,
    'missions_done':    0,
    'tools_collected':  0,
    'endings': {
        'ghost': 0,
        'chaos': 0,
    },
}


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_career() -> Dict:
    """Return the current career stats dict, back-filling missing keys."""
    if not os.path.exists(CAREER_PATH):
        return copy.deepcopy(_DEFAULTS)
    try:
        with open(CAREER_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Back-fill any keys added in later versions
        for k, v in _DEFAULTS.items():
            data.setdefault(k, copy.deepcopy(v))
        return data
    except (json.JSONDecodeError, OSError):
        return copy.deepcopy(_DEFAULTS)


def _save_career(stats: Dict) -> None:
    os.makedirs(os.path.dirname(CAREER_PATH), exist_ok=True)
    with open(CAREER_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def record_run(
    player,
    mode:          str = 'story',
    missions_done: int = 0,
    ending:        str = '',
) -> None:
    """Append run results to the career record.

    Args:
        player:        The Player instance at run end.
        mode:          'story' or 'freelance-N'.
        missions_done: Number of story missions completed this run (0-4).
        ending:        'ghost', 'chaos', or '' for no specific ending.
    """
    stats = load_career()

    if mode == 'story':
        stats['story_runs'] += 1
    else:
        stats['freelance_runs'] += 1

    stats['lifetime_credits'] += player.credits
    stats['best_run']          = max(stats['best_run'], player.credits)
    stats['missions_done']    += missions_done
    stats['tools_collected']  += len(player.tools)

    if ending in stats.get('endings', {}):
        stats['endings'][ending] += 1

    _save_career(stats)


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_career() -> None:
    """Render the career stats screen and wait for Enter."""
    clear_screen()
    print_banner('[ CAREER RECORD ]')
    print()

    stats      = load_career()
    total_runs = stats['story_runs'] + stats['freelance_runs']

    if total_runs == 0:
        slow_print(
            '  No career data yet.\n  '
            'Complete a story run or freelance contract to start tracking.\n',
            delay=0.025,
            colour='dim',
        )
        press_enter()
        return

    rows = [
        ('STORY RUNS COMPLETED',  str(stats['story_runs'])),
        ('FREELANCE CONTRACTS',   str(stats['freelance_runs'])),
        ('LIFETIME CREDITS',      f"{stats['lifetime_credits']:,}"),
        ('BEST SINGLE RUN',       f"{stats['best_run']:,} \u00a2"),
        ('MISSIONS COMPLETED',    str(stats['missions_done'])),
        ('TOOLS COLLECTED',       str(stats['tools_collected'])),
        ('GHOST ENDINGS',         str(stats['endings'].get('ghost', 0))),
        ('CHAOS ENDINGS',         str(stats['endings'].get('chaos', 0))),
    ]

    # Render with a subtle stagger
    for label, value in rows:
        colour_print(f"  {label:<26}  {value}", 'green')
        pause(0.07)

    # Motivational rank line
    print()
    if stats['story_runs'] == 0:
        colour_print("  Complete the story campaign to unlock your full record.", 'dim')
    elif stats['endings'].get('chaos', 0) > stats['endings'].get('ghost', 0):
        colour_print("  Reputation: CHAOS AGENT  — the city remembers.", 'red')
    elif stats['endings'].get('ghost', 0) > 0:
        colour_print("  Reputation: GHOST  — no trace, no name, no face.", 'cyan')
    else:
        colour_print("  Reputation: UNKNOWN  — the board is watching.", 'dim')

    print()
    press_enter()
