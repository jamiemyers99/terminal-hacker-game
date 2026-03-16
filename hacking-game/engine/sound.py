"""
sound.py — Optional audio feedback using platform system sounds.

All functions silently no-op when audio is unavailable or the platform
does not support the required API.  Never raises an exception.

Supported platforms
-------------------
  Windows : winsound.Beep  (built-in, no install required)
  macOS   : afplay with /System/Library/Sounds/  (built-in)
  Linux   : no-op  (no standard audio API without external deps)
"""

import os
import sys


def play_sound(event: str) -> None:
    """Play a short sound for the given game *event*.

    Args:
        event: One of 'success', 'bust', 'menu'.
               Unknown events are silently ignored.
    """
    if os.name == 'nt':
        _play_windows(event)
    elif sys.platform == 'darwin':
        _play_mac(event)
    # Linux / other: silent


# ---------------------------------------------------------------------------
# Platform implementations
# ---------------------------------------------------------------------------

def _play_windows(event: str) -> None:
    """Two-beep sequences via winsound.Beep (frequency Hz, duration ms)."""
    try:
        import winsound
        sequences = {
            'success': [(880, 100), (1100, 160)],
            'bust':    [(300, 200), (180, 350)],
            'menu':    [(600,  80)],
        }
        for freq, dur in sequences.get(event, []):
            winsound.Beep(freq, dur)
    except Exception:
        pass


def _play_mac(event: str) -> None:
    """afplay with bundled macOS system sounds."""
    try:
        import subprocess
        sounds = {
            'success': 'Glass',
            'bust':    'Basso',
            'menu':    'Tink',
        }
        name = sounds.get(event)
        if name:
            subprocess.run(
                ['afplay', f'/System/Library/Sounds/{name}.aiff'],
                capture_output=True,
                timeout=2,
            )
    except Exception:
        pass
