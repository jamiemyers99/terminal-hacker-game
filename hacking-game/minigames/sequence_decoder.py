"""
sequence_decoder.py — Sequence decoder mini-game (breach protocol).

Inspired by the Cyberpunk 2077 breach protocol mechanic:

  • A grid of hex values is displayed alongside a target sequence.
  • Selection alternates between rows and columns:
      - Even turns: player picks a COLUMN from the active row.
      - Odd turns:  player picks a ROW from the active column.
  • A correct pick advances the sequence buffer.
  • A wrong pick costs trace exposure and wastes a move.
  • Win by filling the buffer with all target values inside the move limit.
  • Lose if trace reaches 100 or moves are exhausted.

The target sequence is always generated from a valid path through the grid,
so it is always achievable (though the player may not find it in time).

Difficulty table
----------------
  1 (easy)   : 4×4 grid, 3-value target, 7 moves, +8 trace per wrong
  2 (medium) : 5×5 grid, 4-value target, 8 moves, +12 trace per wrong
  3 (hard)   : 5×5 grid, 4-value target, 6 moves, +15 trace per wrong
"""

import random
from typing import List, Optional, Tuple

from engine.display import colour_print, slow_print, clear_screen, print_banner, print_status_bar
from engine.player  import Player
from engine.utils   import game_input, pause

_HEX_POOL = ['7C', 'E4', '1A', 'FF', '2B', '3D', 'BD', 'A9', '55', 'C0']


# ---------------------------------------------------------------------------
# Grid generation
# ---------------------------------------------------------------------------

def _make_grid(size: int) -> List[List[str]]:
    return [[random.choice(_HEX_POOL) for _ in range(size)] for _ in range(size)]


def _make_solvable_target(
    grid: List[List[str]], target_len: int
) -> Tuple[List[str], List[Tuple[int, int]]]:
    """Return (target_values, solution_path) guaranteed to be achievable.

    The path respects the alternating row/column constraint, starting at row 0.
    """
    size = len(grid)
    path: List[Tuple[int, int]] = []
    current_row = 0
    current_col = 0

    for step in range(target_len):
        if step % 2 == 0:          # even: pick any column in current_row
            col = random.randint(0, size - 1)
            path.append((current_row, col))
            current_col = col
        else:                      # odd: pick any row in current_col
            row = random.randint(0, size - 1)
            path.append((row, current_col))
            current_row = row

    target = [grid[r][c] for r, c in path]
    return target, path


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _render_buffer(target: List[str], buffer: List[str]) -> None:
    t_str = '  '.join(f'[ {v} ]' for v in target)
    b_str = '  '.join(
        f'\033[92m[ {buffer[i]} ]\033[0m' if i < len(buffer) else '\033[2m[ __ ]\033[0m'
        for i in range(len(target))
    )
    colour_print(f"  TARGET : {t_str}", 'yellow')
    colour_print(f"  BUFFER : {b_str}", 'cyan')


def _render_grid(
    grid:         List[List[str]],
    used_cells:   List[Tuple[int, int]],
    current_row:  int,
    current_col:  Optional[int],
    picking_col:  bool,
) -> None:
    """Render the grid with highlights for the active row or column.

    picking_col=True  → player picks a column; active row is highlighted green.
    picking_col=False → player picks a row;    active col is highlighted cyan.
    """
    size = len(grid)
    used_set = set(used_cells)

    # Column index header
    header = '       ' + ''.join(f'  {c}  ' for c in range(size))
    colour_print(header, 'dim')
    colour_print('     ┌' + '─────┬' * (size - 1) + '─────┐', 'dim')

    for r in range(size):
        row_str = f'\033[2m  {r} \033[0m│'

        for c in range(size):
            val     = grid[r][c]
            is_used = (r, c) in used_set
            is_row  = picking_col and r == current_row
            is_col  = (not picking_col) and current_col is not None and c == current_col

            if is_used:
                row_str += f'\033[2m [{val}]\033[0m│'
            elif is_row:
                row_str += f'\033[92m [{val}]\033[0m│'
            elif is_col:
                row_str += f'\033[96m [{val}]\033[0m│'
            else:
                row_str += f'  {val} │'

        # Row/column constraint indicator
        if picking_col and r == current_row:
            row_str += '\033[92m  ← active row\033[0m'
        elif (not picking_col) and current_col is not None:
            pass  # column indicator shown via cell highlights

        print(row_str)

        if r < size - 1:
            colour_print('     ├' + '─────┼' * (size - 1) + '─────┤', 'dim')

    colour_print('     └' + '─────┴' * (size - 1) + '─────┘', 'dim')

    # Active column footer marker
    if not picking_col and current_col is not None:
        marker = '     ' + ' ' * 6 + '     ' * current_col + '  ↑  '
        colour_print(f"{marker}  active column", 'cyan')


# ---------------------------------------------------------------------------
# Public mini-game function
# ---------------------------------------------------------------------------

def sequence_decoder_minigame(difficulty: int, player: Player) -> bool:
    """Run the sequence decoder (breach protocol) mini-game.

    Args:
        difficulty: 1 (easy) → 3 (hard).
        player:     Active Player instance — trace mutated in place.

    Returns:
        True on success, False if caught or moves exhausted.
    """
    size        = 4 if difficulty == 1 else 5
    target_len  = 3 if difficulty == 1 else 4
    max_moves   = {1: 7, 2: 8, 3: 6}.get(difficulty, 7)
    trace_cost  = {1: 8, 2: 12, 3: 15}.get(difficulty, 10)

    grid              = _make_grid(size)
    target, _         = _make_solvable_target(grid, target_len)
    buffer: List[str] = []
    used_cells:  List[Tuple[int, int]] = []
    current_row  = 0
    current_col: Optional[int] = None
    moves_left   = max_moves
    picking_col  = True       # True → pick col from active row; False → pick row from active col
    last_msg     = ''

    # ── Intro ─────────────────────────────────────────────────────────────────
    clear_screen()
    print_banner("[ SEQUENCE DECODER ]")
    slow_print("\n  > BREACH PROTOCOL INITIATED.", delay=0.04, colour='green')
    slow_print("  > ANALYSE THE GRID.  MATCH THE TARGET SEQUENCE.\n", delay=0.04, colour='dim')
    colour_print("  Alternates between picking a COLUMN (from active row)", 'dim')
    colour_print("  and picking a ROW (from active column).\n", 'dim')
    pause(1)

    # ── Main loop ─────────────────────────────────────────────────────────────
    while len(buffer) < target_len and moves_left > 0:
        clear_screen()
        print_banner("[ SEQUENCE DECODER ]")
        print()
        _render_buffer(target, buffer)
        print()
        print_status_bar(player)
        colour_print(f"  MOVES LEFT: {moves_left}\n", 'dim')
        _render_grid(grid, used_cells, current_row, current_col, picking_col)
        print()

        if last_msg:
            colour_print(f"  {last_msg}", 'red')
            last_msg = ''

        if picking_col:
            prompt = f"  Select COLUMN (0–{size - 1})  from ROW {current_row}:"
        else:
            prompt = f"  Select ROW (0–{size - 1})  from COLUMN {current_col}:"

        colour_print(prompt, 'cyan')
        raw = game_input("\033[96m  > \033[0m", player).strip()

        if not raw.isdigit():
            last_msg = "[!] Enter a number."
            continue

        idx = int(raw)
        if not (0 <= idx < size):
            last_msg = f"[!] Out of range — must be 0 to {size - 1}."
            continue

        # ── Resolve selected cell ─────────────────────────────────────────────
        if picking_col:
            r, c   = current_row, idx
            current_col = idx
        else:
            r, c   = idx, current_col
            current_row = idx

        used_cells.append((r, c))
        val        = grid[r][c]
        moves_left -= 1
        picking_col = not picking_col

        # ── Check value ───────────────────────────────────────────────────────
        expected = target[len(buffer)]
        if val == expected:
            buffer.append(val)
            colour_print(f"\n  [+] Match: {val}  ✓", 'green')
        else:
            caught = player.increase_trace(trace_cost)
            last_msg = (
                f"[!] No match — got {val},  expected {expected}.  "
                f"Trace +{trace_cost}"
            )
            if caught:
                clear_screen()
                slow_print(
                    "\n  > TRACE COMPLETE.  SEQUENCE ABORTED.\n",
                    delay=0.04, colour='red'
                )
                pause(0.5)
                return False

        pause(0.35)

    # ── Outcome ───────────────────────────────────────────────────────────────
    if len(buffer) == target_len:
        clear_screen()
        slow_print("\n  > SEQUENCE MATCHED.  BREACH SUCCESSFUL.\n",
                   delay=0.04, colour='green')
        pause(0.5)
        return True

    slow_print(
        "\n  > MOVE LIMIT REACHED.  SEQUENCE INCOMPLETE.\n",
        delay=0.04, colour='red'
    )
    pause(0.5)
    return False
