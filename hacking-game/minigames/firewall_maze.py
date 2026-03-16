"""
firewall_maze.py — Firewall bypass maze mini-game.

A random maze is generated using depth-first search (recursive backtracker).
The player navigates from the top-left to the bottom-right exit using
W/A/S/D keys (or arrow keys).  Trace exposure increases every N steps — the
player must reach the exit before being detected.

Rendering key
-------------
  ██  = wall / firewall node
  (space)(space) = open corridor
  ()  = player position  (green)
  ><  = exit             (yellow)

Difficulty / size table
-----------------------
  size 1 (easy)   : 5×5 cells,  trace +6 every 5 steps
  size 2 (medium) : 7×7 cells,  trace +9 every 4 steps
  size 3 (hard)   : 9×9 cells,  trace +12 every 3 steps
"""

import os
import random
import sys
from typing import List, Optional, Tuple

from engine.display import colour_print, slow_print, clear_screen, print_banner, print_status_bar, show_inventory
from engine.player  import Player
from engine.utils   import pause

_WALL = '#'
_PATH = ' '


# ---------------------------------------------------------------------------
# Maze generation — recursive DFS backtracker
# ---------------------------------------------------------------------------

def _generate_maze(rows: int, cols: int) -> List[List[str]]:
    """Return a (rows*2+1) × (cols*2+1) grid where '#' = wall and ' ' = path.

    Uses a recursive DFS to carve passages so every cell is reachable.
    """
    height = rows * 2 + 1
    width  = cols * 2 + 1
    maze   = [[_WALL] * width for _ in range(height)]
    visited = [[False] * cols for _ in range(rows)]

    def dfs(r: int, c: int) -> None:
        visited[r][c] = True
        maze[r * 2 + 1][c * 2 + 1] = _PATH
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                maze[r * 2 + 1 + dr][c * 2 + 1 + dc] = _PATH   # knock down wall
                dfs(nr, nc)

    dfs(0, 0)
    return maze


# ---------------------------------------------------------------------------
# Key input — single keypress without requiring Enter
# ---------------------------------------------------------------------------

def _get_key() -> str:
    """Block until a single keypress and return it as a lowercase string.

    Supports W/A/S/D, arrow keys, and Q.
    Falls back to line-buffered input() on platforms where raw mode is
    unavailable.
    """
    if os.name == 'nt':
        try:
            import msvcrt
            ch = msvcrt.getch()
            if ch in (b'\xe0', b'\x00'):          # extended key prefix
                ch2 = msvcrt.getch()
                return {b'H': 'w', b'P': 's', b'K': 'a', b'M': 'd'}.get(ch2, '')
            try:
                return ch.decode('utf-8').lower()
            except UnicodeDecodeError:
                return ''
        except Exception:
            pass
    else:
        try:
            import tty
            import termios
            fd  = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    rest = sys.stdin.read(2)
                    seq  = ch + rest
                    return {'\x1b[A': 'w', '\x1b[B': 's',
                            '\x1b[D': 'a', '\x1b[C': 'd'}.get(seq, '')
                return ch.lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass

    # Fallback: line-buffered input
    try:
        raw = input().strip().lower()
        return raw[0] if raw else ''
    except (EOFError, KeyboardInterrupt):
        return 'q'


# ---------------------------------------------------------------------------
# Maze renderer
# ---------------------------------------------------------------------------

def _render_maze(
    maze:     List[List[str]],
    player_r: int,
    player_c: int,
    exit_r:   int,
    exit_c:   int,
) -> None:
    """Print the maze to stdout.  Each grid cell is rendered 2 chars wide."""
    grid_rows = len(maze)
    grid_cols = len(maze[0])

    pr = player_r * 2 + 1
    pc = player_c * 2 + 1
    er = exit_r   * 2 + 1
    ec = exit_c   * 2 + 1

    for r in range(grid_rows):
        row_str = '  '
        for c in range(grid_cols):
            if r == pr and c == pc:
                row_str += '\033[92m()\033[0m'          # player — green
            elif r == er and c == ec:
                row_str += '\033[93m><\033[0m'          # exit   — yellow
            elif maze[r][c] == _WALL:
                row_str += '\033[92m██\033[0m'          # wall   — dark green
            else:
                row_str += '  '                         # open corridor
        print(row_str)


# ---------------------------------------------------------------------------
# Public mini-game function
# ---------------------------------------------------------------------------

def firewall_maze_minigame(size: int, player: Player) -> bool:
    """Run the firewall bypass maze mini-game.

    Args:
        size:   Difficulty level: 1 (5×5), 2 (7×7), 3 (9×9).
        player: Active Player instance — trace mutated in place.

    Returns:
        True if the player reached the exit, False if caught or aborted.
    """
    cell_size       = {1: 5, 2: 7, 3: 9}.get(size, 5)
    trace_interval  = {1: 5, 2: 4, 3: 3}.get(size, 5)
    trace_amount    = {1: 6, 2: 9, 3: 12}.get(size, 6)

    maze   = _generate_maze(cell_size, cell_size)
    pr, pc = 0, 0                              # player cell position
    er, ec = cell_size - 1, cell_size - 1      # exit cell position
    steps  = 0
    msg    = ''                                # inline feedback line

    dir_map = {
        'w': (-1,  0),
        's': ( 1,  0),
        'a': ( 0, -1),
        'd': ( 0,  1),
    }

    # ── Intro screen ──────────────────────────────────────────────────────────
    clear_screen()
    print_banner("[ FIREWALL BYPASS ]")
    slow_print("\n  > MAPPING FIREWALL TOPOLOGY...", delay=0.04, colour='green')
    slow_print("  > ROUTE TO EXIT BEFORE TRACE COMPLETES.\n", delay=0.04, colour='dim')
    colour_print("  ()  =  YOU    ><  =  EXIT    ██  =  FIREWALL NODE", 'dim')
    colour_print("  CONTROLS:  W A S D  or  ARROW KEYS   |   I = inventory   |   Q = abort\n", 'dim')
    pause(1)

    # ── Navigation loop ───────────────────────────────────────────────────────
    while True:
        clear_screen()
        print_banner("[ FIREWALL BYPASS ]")
        print()
        print_status_bar(player)
        colour_print(
            f"  STEPS: {steps}   |   "
            f"Trace increases every {trace_interval} steps  (+{trace_amount})\n",
            'dim'
        )
        _render_maze(maze, pr, pc, er, ec)
        print()

        if msg:
            colour_print(f"  {msg}", 'red')
            msg = ''
        else:
            colour_print("  MOVE: W/A/S/D", 'dim')

        key = _get_key()

        # ── Inventory ─────────────────────────────────────────────────────────
        if key == 'i':
            show_inventory(player)
            continue

        # ── Abort ─────────────────────────────────────────────────────────────
        if key == 'q':
            colour_print("\n  [!] Aborting connection...\n", 'red')
            pause(0.5)
            return False

        # ── Invalid key ───────────────────────────────────────────────────────
        if key not in dir_map:
            continue

        dr, dc = dir_map[key]
        nr, nc = pr + dr, pc + dc

        # ── Bounds check ──────────────────────────────────────────────────────
        if not (0 <= nr < cell_size and 0 <= nc < cell_size):
            msg = "[!] EDGE OF MAP."
            continue

        # ── Wall check ────────────────────────────────────────────────────────
        wall_r = pr * 2 + 1 + dr
        wall_c = pc * 2 + 1 + dc
        if maze[wall_r][wall_c] == _WALL:
            msg = "[!] FIREWALL NODE DETECTED — path blocked."
            continue

        # ── Valid move ────────────────────────────────────────────────────────
        pr, pc  = nr, nc
        steps  += 1

        # ── Periodic trace increase ───────────────────────────────────────────
        if steps % trace_interval == 0:
            caught = player.increase_trace(trace_amount)
            if caught:
                clear_screen()
                slow_print(
                    "\n  > TRACE COMPLETE.  NEURAL LINK SEVERED.\n",
                    delay=0.04, colour='red'
                )
                pause(0.5)
                return False

        # ── Win condition ─────────────────────────────────────────────────────
        if pr == er and pc == ec:
            clear_screen()
            print_banner("[ FIREWALL BYPASS ]")
            slow_print("\n  > EXIT NODE REACHED.", delay=0.04, colour='green')
            slow_print("  > FIREWALL CIRCUMVENTED.  ROUTE SECURED.\n",
                       delay=0.04, colour='green')
            pause(0.5)
            return True
