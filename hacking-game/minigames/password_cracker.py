"""
password_cracker.py — Password cracking mini-game.

The player must guess a hidden password drawn from a wordlist.  Wrong guesses
increase trace exposure.  Type 'hint' at any prompt to reveal one letter at a
higher trace cost.

Difficulty table
----------------
  1 (easy)   : easy words,   8 guesses, +5 trace per wrong,  +10 for hint
  2 (medium) : medium words, 6 guesses, +10 trace per wrong, +15 for hint
  3 (hard)   : hard words,   4 guesses, +15 trace per wrong, +20 for hint
"""

import json
import os
import random
from typing import List

from engine.display import colour_print, slow_print, clear_screen, print_banner, print_status_bar
from engine.player  import Player
from engine.utils   import game_input, pause

_GAME_ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORDLIST_PATH = os.path.join(_GAME_ROOT, 'data', 'wordlists.json')


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_wordlist(difficulty: int) -> List[str]:
    key = {1: 'easy', 2: 'medium', 3: 'hard'}.get(min(max(difficulty, 1), 3), 'easy')
    try:
        with open(_WORDLIST_PATH, 'r', encoding='utf-8') as f:
            return json.load(f).get(key, [])
    except (FileNotFoundError, json.JSONDecodeError):
        return ['ghost', 'cipher', 'signal', 'system', 'kernel']


def _build_hint(target: str, difficulty: int) -> str:
    parts = [f"{len(target)} letters"]
    if difficulty == 1:
        parts.append(f"starts with '{target[0].upper()}'")
    elif difficulty == 2:
        parts.append(f"{len(set(target))} unique characters")
    return ',  '.join(parts)


def _score_guess(guess: str, target: str):
    """Return (correct_positions, letters_in_word) counts — Wordle-style feedback."""
    correct_pos = sum(a == b for a, b in zip(guess, target))
    in_word     = sum(min(guess.count(c), target.count(c)) for c in set(guess))
    return correct_pos, in_word


def _mask(target: str, revealed: set) -> str:
    return ' '.join(c.upper() if i in revealed else '_' for i, c in enumerate(target))


# ---------------------------------------------------------------------------
# Public mini-game function
# ---------------------------------------------------------------------------

def password_crack_minigame(difficulty: int, player: Player) -> bool:
    """Run the password cracker mini-game.

    Args:
        difficulty: 1 (easy) → 3 (hard).
        player:     Active Player instance — trace will be mutated in place.

    Returns:
        True if the password was cracked, False if the player was caught.
    """
    wordlist        = _load_wordlist(difficulty)
    target          = random.choice(wordlist)
    max_guesses     = {1: 8, 2: 6, 3: 4}.get(difficulty, 6)
    trace_per_wrong = {1: 5, 2: 10, 3: 15}.get(difficulty, 10)
    trace_per_hint  = trace_per_wrong + 5
    hint_str        = _build_hint(target, difficulty)
    revealed        = set()          # indices of characters the player has revealed

    # ── Header ───────────────────────────────────────────────────────────────
    clear_screen()
    print_banner("[ PASSWORD CRACKER ]")
    slow_print("\n  > INITIATING BRUTE FORCE ATTACK...", delay=0.04, colour='green')
    slow_print("  > WORDLIST LOADED.  STANDING BY.\n",  delay=0.04, colour='dim')
    colour_print(f"  HINT     :  {hint_str}", 'yellow')
    colour_print(f"  ATTEMPTS :  {max_guesses} allowed", 'cyan')
    colour_print(f"\n  Type  'hint'  to reveal one letter  (+{trace_per_hint} trace)\n", 'dim')
    pause(0.3)

    # ── Guess loop ────────────────────────────────────────────────────────────
    for attempt in range(1, max_guesses + 1):
        print_status_bar(player)

        if revealed:
            colour_print(f"  MASK     :  {_mask(target, revealed)}", 'cyan')

        colour_print(f"\n  Attempt {attempt} / {max_guesses}", 'dim')
        guess = game_input("\033[96m  > \033[0m", player).strip().lower()

        if not guess:
            continue

        # ── Hint request ─────────────────────────────────────────────────────
        if guess == 'hint':
            unrevealed = [i for i in range(len(target)) if i not in revealed]
            if not unrevealed:
                colour_print("  [!] All letters already revealed.", 'yellow')
                continue
            caught = player.increase_trace(trace_per_hint)
            idx    = random.choice(unrevealed)
            revealed.add(idx)
            colour_print(
                f"  [HINT] Position {idx + 1}: '{target[idx].upper()}'  "
                f"(trace +{trace_per_hint})",
                'yellow'
            )
            if caught:
                slow_print("\n  > TRACE COMPLETE.  CONNECTION TERMINATED.\n",
                           delay=0.04, colour='red')
                return False
            continue

        # ── Correct guess ─────────────────────────────────────────────────────
        if guess == target:
            colour_print("\n  > MATCH FOUND.", 'green')
            slow_print(
                "  > PASSWORD ACCEPTED.  AUTHENTICATION BYPASSED.\n",
                delay=0.04, colour='green'
            )
            pause(0.5)
            return True

        # ── Wrong guess ───────────────────────────────────────────────────────
        correct_pos, in_word = _score_guess(guess, target)
        caught = player.increase_trace(trace_per_wrong)

        colour_print(
            f"  [!] INCORRECT  —  "
            f"Letters in correct position: {correct_pos}  |  "
            f"Letters in word: {in_word}",
            'red'
        )
        colour_print(f"      Trace +{trace_per_wrong}", 'dim')

        if caught:
            slow_print(
                "\n  > TRACE COMPLETE.  LOCKOUT INITIATED.\n",
                delay=0.04, colour='red'
            )
            return False

        print()

    # ── Out of guesses ────────────────────────────────────────────────────────
    slow_print(
        f"\n  > MAX ATTEMPTS REACHED.  Password was: {target.upper()}\n",
        delay=0.04, colour='red'
    )
    pause(0.5)
    return False
