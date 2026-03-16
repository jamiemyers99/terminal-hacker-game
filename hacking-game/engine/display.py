"""
display.py — Terminal output utilities.

Provides typewriter printing, ANSI colour output, screen clearing,
banner rendering, the trace/status bar, inventory overlay, and the
end-game credits screen.
"""

import os
import sys
import time

# ---------------------------------------------------------------------------
# ANSI colour map
# ---------------------------------------------------------------------------

COLOURS = {
    'green':  '\033[92m',
    'red':    '\033[91m',
    'cyan':   '\033[96m',
    'yellow': '\033[93m',
    'white':  '\033[97m',
    'magenta':'\033[95m',
    'dim':    '\033[2m',
    'bold':   '\033[1m',
    'reset':  '\033[0m',
}


def _enable_ansi() -> None:
    """Enable ANSI escape codes on Windows where needed."""
    if os.name == 'nt':
        try:
            import colorama
            colorama.init(autoreset=False)
        except ImportError:
            # Fall back to Win32 VT100 mode (Windows 10+)
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception:
                pass


_enable_ansi()


# ---------------------------------------------------------------------------
# Skip-key detection (non-blocking)
# ---------------------------------------------------------------------------

def _check_skip() -> bool:
    """Non-blocking check: return True if Enter or Space has been pressed.

    Used by slow_print to let the player skip past typewriter text instantly.
    Consumes the keypress so it does not bleed into the next input() call.
    """
    if os.name == 'nt':
        try:
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                return key in (b'\r', b'\n', b' ')
        except Exception:
            pass
    else:
        try:
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                return ch in ('\r', '\n', ' ')
        except Exception:
            pass
    return False


# ---------------------------------------------------------------------------
# Core output functions
# ---------------------------------------------------------------------------

def slow_print(text: str, delay: float = 0.03, colour: str = None, end: str = '\n') -> None:
    """Print *text* character by character for a typewriter effect.

    The player can press Enter or Space at any point to flush the remaining
    characters instantly (skip mode).

    Args:
        text:   The string to display.
        delay:  Seconds between each character (default 0.03).
        colour: Optional colour key from COLOURS dict.
        end:    Character appended after the final character (default newline).
    """
    code  = COLOURS.get(colour, '') if colour else ''
    reset = COLOURS['reset']         if colour else ''
    if code:
        sys.stdout.write(code)
    skipped = False
    for char in text:
        if not skipped and _check_skip():
            skipped = True
        sys.stdout.write(char)
        sys.stdout.flush()
        if not skipped:
            time.sleep(delay)
    sys.stdout.write(reset + end)
    sys.stdout.flush()


def colour_print(text: str, colour: str, end: str = '\n') -> None:
    """Print *text* wrapped in the given ANSI colour, then reset."""
    code  = COLOURS.get(colour, '')
    reset = COLOURS['reset']
    print(f"{code}{text}{reset}", end=end)


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner(title: str, width: int = 58) -> None:
    """Print a centred double-line box banner with *title* inside.

    Args:
        title: The text to centre inside the banner.
        width: Total width of the banner including border characters.
    """
    inner    = width - 2
    border   = '═' * inner
    pad_total = inner - len(title) - 2      # -2 for the spaces either side
    pad_left  = pad_total // 2
    pad_right = pad_total - pad_left
    colour_print(f"╔{border}╗", 'green')
    colour_print(f"║{' ' * pad_left} {title} {' ' * pad_right}║", 'green')
    colour_print(f"╚{border}╝", 'green')


def print_trace_bar(trace: int, width: int = 20) -> None:
    """Print a visual trace exposure bar to the terminal.

    Example output:
        TRACE: [██████░░░░░░░░░░░░░░] 30%

    Args:
        trace: Current trace value (0–100).
        width: Number of bar segments.
    """
    filled  = int((max(0, min(100, trace)) / 100) * width)
    empty   = width - filled
    bar     = '█' * filled + '░' * empty
    colour  = 'green' if trace < 50 else ('yellow' if trace < 80 else 'red')
    colour_print(f"  TRACE: [{bar}] {trace}%", colour)


def print_section(label: str, width: int = 50) -> None:
    """Print a labelled divider line, e.g. ── INVENTORY ──────"""
    colour_print(f"\n  ── {label} {'─' * (width - len(label) - 4)}", 'dim')


# ---------------------------------------------------------------------------
# Status bar
# ---------------------------------------------------------------------------

def print_status_bar(player) -> None:
    """Print a combined one-line player info strip followed by the trace bar.

    Example output:
        Ghost  |  Lv.2  |  750¢  |  2 tools
        TRACE: [████████░░░░░░░░░░░░] 40%

    Accepts the Player instance directly so callers don't have to destructure.
    """
    tool_count = len(player.tools)
    tool_str   = f"{tool_count} tool{'s' if tool_count != 1 else ''}"
    info = (
        f"  \033[2m{player.name}  |  Lv.{player.level}  |  "
        f"{player.credits}\u00a2  |  {tool_str}\033[0m"
    )
    print(info)
    print_trace_bar(player.trace_exposure)


# ---------------------------------------------------------------------------
# In-game inventory overlay
# ---------------------------------------------------------------------------

# Inner content width (chars between the ║  …  ║ borders).
_INV_CONTENT = 46

# Box border width = content + 4 padding chars (2 each side).
_INV_BORDER  = _INV_CONTENT + 4


def _irow(text: str = '') -> str:
    """Return one inventory box row, padding/truncating *text* to fit."""
    return f"  \u2551  {text[:_INV_CONTENT].ljust(_INV_CONTENT)}  \u2551"


_TOOL_DESC = {
    'port_scanner': 'Port Scanner   — passive trace buffer  (-15)',
    'vpn_shield':   'VPN Shield     — halves trace gain  [single-use]',
    'root_kit':     'Root Kit       — auto-solves one stage  [single-use]',
}


def show_inventory(player) -> None:
    """Print the player's toolkit as an inline overlay box.

    Prompts for Enter before returning so the caller's screen is not
    immediately overwritten.
    """
    from engine.utils import safe_input   # local import avoids circular dep

    border  = f"  \u2554{'═' * _INV_BORDER}\u2557"
    divider = f"  \u2560{'═' * _INV_BORDER}\u2563"
    bottom  = f"  \u255a{'═' * _INV_BORDER}\u255d"

    print()
    colour_print(border,  'yellow')
    colour_print(_irow("  T O O L K I T"), 'yellow')
    colour_print(divider, 'yellow')

    if not player.tools:
        colour_print(_irow("  (no tools collected yet)"), 'dim')
    else:
        for tool in player.tools:
            colour_print(_irow(f"  \u25b8  {_TOOL_DESC.get(tool, tool)}"), 'cyan')

    colour_print(divider, 'yellow')
    colour_print(_irow(f"  Credits : {player.credits}"), 'yellow')
    colour_print(_irow(f"  Level   : {player.level}"), 'yellow')
    colour_print(bottom,  'yellow')
    print()
    safe_input('\033[2m  Press ENTER to return...\033[0m')
    print()


# ---------------------------------------------------------------------------
# End-game credits screen
# ---------------------------------------------------------------------------

def show_credits_screen(player) -> None:
    """Display the full end-game scrolling credits sequence.

    Shows the game logo, player stats, and a scrolling credits block,
    then waits for Enter before returning to the main menu.
    """
    from engine.utils   import pause, press_enter   # local import
    from assets.ascii_art import GAME_LOGO, ACCESS_GRANTED

    # ── ACCESS GRANTED flash ──────────────────────────────────────────────────
    clear_screen()
    print(ACCESS_GRANTED)
    pause(2.0)

    # ── Main credits screen ───────────────────────────────────────────────────
    clear_screen()
    print(GAME_LOGO)

    div = '  ' + '═' * 58
    colour_print(div, 'green')
    pause(0.3)

    stats = [
        ('HACKER ALIAS', player.name),
        ('MISSIONS',     '4 / 4  complete'),
        ('FINAL SCORE',  f'{player.credits} credits'),
        ('ARSENAL',      ', '.join(player.tools) if player.tools else 'none'),
    ]
    for label, value in stats:
        slow_print(f"  {label:<16}: {value}", delay=0.02, colour='green')
        pause(0.08)

    colour_print(div, 'green')
    pause(0.5)

    # ── Scrolling credits block ───────────────────────────────────────────────
    credit_lines = [
        '',
        '  Developed with Python 3',
        '  No external dependencies required',
        '',
        f"  {'─' * 44}",
        '',
        '  "The ghost in the machine was you."',
        '',
        f"  {'─' * 44}",
        '',
        '                  Thank you for playing.',
        '',
        '',
    ]
    for line in credit_lines:
        colour_print(line, 'dim')
        pause(0.18)

    press_enter('  [ Press ENTER to return to the main menu... ]')
