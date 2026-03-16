"""
utils.py — Shared helper utilities used across the engine and game modules.
"""

import os
import sys
import time


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def sanitise_input(raw: str) -> str:
    """Strip surrounding whitespace and normalise to lowercase."""
    return raw.strip().lower()


def safe_input(prompt: str = '') -> str:
    """Input wrapper that handles KeyboardInterrupt and EOFError gracefully.

    Returns an empty string on interruption rather than crashing.
    """
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print('\n\033[91m[!] Interrupted.\033[0m')
        return ''
    except EOFError:
        return ''


def pause(seconds: float = 1.0) -> None:
    """Sleep for *seconds*."""
    time.sleep(seconds)


def press_enter(message: str = 'Press ENTER to continue...') -> None:
    """Display *message* and wait for the user to press Enter."""
    safe_input(f'\033[2m  {message}\033[0m')


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Return *value* clamped to the range [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def centre_text(text: str, width: int = 60) -> str:
    """Return *text* padded with spaces to sit centred within *width* chars."""
    return text.center(width)


def game_input(prompt: str = '', player=None) -> str:
    """Like safe_input, but intercepts 't' to show the player's toolkit.

    If the user types 't' (or 'T') at any prompt that uses this function,
    the inventory overlay is displayed and the prompt is repeated.

    Args:
        prompt: The input prompt string (same as safe_input).
        player: The active Player instance, or None to disable the intercept.

    Returns:
        The raw user input string (not stripped or lowercased).
    """
    while True:
        raw = safe_input(prompt)
        if player is not None and raw.strip().lower() == 't':
            from engine.display import show_inventory
            show_inventory(player)
        else:
            return raw
