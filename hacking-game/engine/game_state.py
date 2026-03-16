"""
game_state.py — Save / load / delete game state via JSON.

Save file location: data/save.json (relative to the hacking-game/ root).
"""

import json
import os
from typing import Optional

from engine.player import Player

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_GAME_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH  = os.path.join(_GAME_ROOT, 'data', 'save.json')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_game(player: Player, current_mission: str) -> None:
    """Serialise *player* state and the current mission ID to disk.

    Creates data/ directory automatically if it doesn't exist.
    """
    state = {
        'player':          player.to_dict(),
        'current_mission': current_mission,
    }
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def load_game() -> Optional[dict]:
    """Read and return the raw state dict from data/save.json.

    Returns None if the file doesn't exist or is corrupt.
    """
    if not os.path.exists(SAVE_PATH):
        return None
    try:
        with open(SAVE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def delete_save() -> bool:
    """Delete data/save.json. Returns True if the file existed."""
    if os.path.exists(SAVE_PATH):
        os.remove(SAVE_PATH)
        return True
    return False


def save_exists() -> bool:
    """Return True if a save file is present on disk."""
    return os.path.exists(SAVE_PATH)
