"""
leaderboard.py — Local high score leaderboard.

Stores the top MAX_ENTRIES scores in data/leaderboard.json.
Tracks both story completions and freelance contract runs.

Entry schema
------------
{
    "alias":    str,   # hacker alias, truncated to 16 chars
    "score":    int,   # credits earned in the run
    "missions": int,   # story missions completed (0-4)
    "mode":     str,   # "story" | "freelance-1" | "freelance-2" | "freelance-3"
    "date":     str,   # ISO date string YYYY-MM-DD
}
"""

import json
import os
from datetime import date
from typing   import Dict, List

from engine.display import colour_print, clear_screen, print_banner
from engine.utils   import press_enter, pause

_GAME_ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADERBOARD_PATH = os.path.join(_GAME_ROOT, 'data', 'leaderboard.json')
MAX_ENTRIES      = 10


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def load_scores() -> List[Dict]:
    """Return all stored score entries, sorted highest-first."""
    if not os.path.exists(LEADERBOARD_PATH):
        return []
    try:
        with open(LEADERBOARD_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_scores(entries: List[Dict]) -> None:
    os.makedirs(os.path.dirname(LEADERBOARD_PATH), exist_ok=True)
    with open(LEADERBOARD_PATH, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_high_score(score: int) -> bool:
    """Return True if *score* would place in the top MAX_ENTRIES."""
    entries = load_scores()
    if len(entries) < MAX_ENTRIES:
        return True
    return score > entries[-1]['score']


def add_entry(
    alias:              str,
    score:              int,
    missions_completed: int,
    mode:               str = 'story',
) -> int:
    """Insert a new entry, keep only the top MAX_ENTRIES, and persist.

    Returns the 1-based rank of the new entry, or 0 if it fell outside
    the top 10 (edge case if score ties push it out).
    """
    today   = str(date.today())
    entries = load_scores()
    entry   = {
        'alias':    alias[:16],
        'score':    score,
        'missions': missions_completed,
        'mode':     mode,
        'date':     today,
    }
    entries.append(entry)
    entries.sort(key=lambda x: x['score'], reverse=True)
    entries = entries[:MAX_ENTRIES]
    _save_scores(entries)

    for i, e in enumerate(entries):
        if e['alias'] == entry['alias'] and e['score'] == score and e['date'] == today:
            return i + 1
    return 0


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_leaderboard() -> None:
    """Render the full leaderboard screen and wait for Enter."""
    clear_screen()
    print_banner('[ HIGH SCORES ]')
    print()

    entries = load_scores()
    if not entries:
        colour_print('  No scores recorded yet.', 'dim')
        colour_print(
            '  Complete a story run or freelance contract to get on the board.\n',
            'dim',
        )
        press_enter()
        return

    # Column header
    colour_print(
        f"  {'#':<4} {'ALIAS':<17} {'SCORE':>9}  {'MODE':<14} DATE",
        'cyan',
    )
    colour_print('  ' + '─' * 58, 'dim')

    # One colour per rank tier: gold, silver/bronze, then dim
    rank_colours = ['yellow', 'white', 'white'] + ['dim'] * (MAX_ENTRIES - 3)

    for i, e in enumerate(entries):
        # Friendly mode label
        mode_raw = e.get('mode', 'story')
        if mode_raw == 'story':
            mode_label = f"story  ({e['missions']}/4)"
        else:
            tier = mode_raw.replace('freelance-', '')
            tier_names = {'1': 'low', '2': 'mid', '3': 'high'}
            mode_label = f"contract ({tier_names.get(tier, tier)})"

        colour_print(
            f"  {str(i + 1) + '.':<4} "
            f"{e['alias']:<17} "
            f"{e['score']:>9,}  "
            f"{mode_label:<14} "
            f"{e['date']}",
            rank_colours[i],
        )

    print()
    press_enter()
