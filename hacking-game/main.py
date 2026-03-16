#!/usr/bin/env python3
"""
main.py — Terminal Hacking Game entry point.

Bootstraps the Python path, displays the title screen, and routes the
player through the main menu into the mission runner.
"""

import os
import sys

# Ensure the hacking-game/ directory is importable regardless of how the
# script is launched (e.g. `python main.py` from within or above the folder).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.display      import colour_print, slow_print, clear_screen, show_credits_screen
from engine.player       import Player
from engine.game_state   import save_game, load_game, delete_save, save_exists
from engine.utils        import safe_input, pause, press_enter
from engine.sound        import play_sound
from engine.leaderboard  import is_high_score, add_entry, display_leaderboard
from engine.career       import record_run, display_career
from assets.ascii_art    import GAME_LOGO


# ---------------------------------------------------------------------------
# Mission registry
# ---------------------------------------------------------------------------
# Each entry maps a mission_id → (MissionClass, next_mission_id | None).
# New missions are added here as they are built in Phase 3+.

def _build_mission_registry() -> dict:
    registry = {}
    try:
        from missions.the_leak import TheLeak
        registry['mission_1'] = (TheLeak, 'mission_2')
    except ImportError:
        pass
    try:
        from missions.follow_the_money import FollowTheMoney
        registry['mission_2'] = (FollowTheMoney, 'mission_3')
    except ImportError:
        pass
    try:
        from missions.ghost_protocol import GhostProtocol
        registry['mission_3'] = (GhostProtocol, 'mission_4')
    except ImportError:
        pass
    try:
        from missions.zero_day import ZeroDay
        registry['mission_4'] = (ZeroDay, None)
    except ImportError:
        pass
    return registry


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def show_logo() -> None:
    clear_screen()
    print(GAME_LOGO)
    pause(0.5)


def show_main_menu() -> str:
    play_sound('menu')
    colour_print('  ┌──────────────────────────────────┐', 'cyan')
    colour_print('  │   [1]  New Game                  │', 'cyan')
    colour_print('  │   [2]  Load Game                 │', 'cyan')
    colour_print('  │   [3]  Freelance Run              │', 'cyan')
    colour_print('  │   [4]  Leaderboard               │', 'cyan')
    colour_print('  │   [5]  Career                    │', 'cyan')
    colour_print('  │   [6]  Quit                      │', 'cyan')
    colour_print('  └──────────────────────────────────┘', 'cyan')
    print()
    return safe_input('\033[92m  > \033[0m').strip()


# ---------------------------------------------------------------------------
# New / load game
# ---------------------------------------------------------------------------

def start_new_game() -> Player:
    clear_screen()
    colour_print('\n  [ INITIATE NEW SESSION ]\n', 'green')
    name = safe_input('\033[96m  Enter your hacker alias: \033[0m').strip()
    if not name:
        name = 'Ghost'
    player = Player(name)
    print()
    slow_print(f'  Alias accepted: {player.name}', delay=0.04, colour='green')
    slow_print('  Neural link established.', delay=0.04, colour='green')
    slow_print('  Your terminal is your weapon. Use it wisely.\n', delay=0.04, colour='dim')
    pause(1)
    return player


def load_existing_game():
    """Return (Player, mission_id) from save, or (None, None) on failure."""
    data = load_game()
    if data is None:
        colour_print('\n  [!] No save file found.\n', 'red')
        pause(1)
        return None, None
    player     = Player.from_dict(data['player'])
    mission_id = data.get('current_mission', 'mission_1')
    colour_print(
        f'\n  [+] Session restored: {player.name}  |  '
        f'Level {player.level}  |  {player.credits} credits\n',
        'green'
    )
    pause(1)
    return player, mission_id


# ---------------------------------------------------------------------------
# Mission runner
# ---------------------------------------------------------------------------

def run_missions(player: Player, start_mission: str = 'mission_1') -> None:
    registry = _build_mission_registry()

    if not registry:
        _show_no_missions_stub()
        return

    current_id    = start_mission
    missions_done = 0

    while current_id and current_id in registry:
        mission_cls, next_id = registry[current_id]
        mission = mission_cls(player)

        mission.start()
        press_enter('  [ READY TO CONNECT? ] Press ENTER...')

        result = mission.run()
        save_game(player, current_id)

        if result:
            mission.complete()
            missions_done += 1
            pause(2)
            current_id = next_id        # advance to next mission
        else:
            mission.fail()
            colour_print('\n  Regrouping — retrying mission...\n', 'yellow')
            pause(2)
            # Stay on the same mission; player retries until success

    # Detect ending via player state (zero_day sets a flag if it implements one,
    # otherwise derive it from credits as a reasonable proxy)
    ending = getattr(player, 'ending', '')
    _show_end_screen(player, missions_done=missions_done, ending=ending)


def _show_no_missions_stub() -> None:
    """Placeholder shown when no mission modules have been built yet."""
    colour_print('\n  [ MISSION UPLINK UNAVAILABLE ]\n', 'cyan')
    slow_print('  No mission files found.', delay=0.03, colour='dim')
    slow_print('  Phase 3 development in progress.\n', delay=0.03, colour='dim')
    press_enter()


def _offer_leaderboard_entry(player: Player, mode: str, missions_done: int = 0) -> None:
    """Prompt for alias and submit to leaderboard if score qualifies."""
    if player.credits <= 0:
        return
    if not is_high_score(player.credits):
        colour_print('\n  Score did not crack the top 10 this time.\n', 'dim')
        return

    colour_print('\n  *** NEW HIGH SCORE ***\n', 'yellow')
    alias = safe_input('\033[96m  Enter alias for the leaderboard (blank = your name): \033[0m').strip()
    if not alias:
        alias = player.name
    rank = add_entry(alias, player.credits, missions_done, mode)
    if rank:
        colour_print(f'\n  [+] Entered at rank #{rank}. Glory is yours.\n', 'green')
    pause(1)


def _show_end_screen(player: Player, missions_done: int = 0, ending: str = '') -> None:
    record_run(player, mode='story', missions_done=missions_done, ending=ending)
    show_credits_screen(player)
    _offer_leaderboard_entry(player, mode='story', missions_done=missions_done)
    delete_save()


# ---------------------------------------------------------------------------
# Freelance mode
# ---------------------------------------------------------------------------

def run_freelance_mode() -> None:
    """Standalone freelance contract — one-shot, no save state."""
    try:
        from missions.freelance import FreelanceMission
    except ImportError:
        colour_print('\n  [!] Freelance module unavailable.\n', 'red')
        pause(1)
        return

    clear_screen()
    colour_print('\n  [ FREELANCE CONTRACT BROKER ]\n', 'green')
    colour_print('  Select difficulty tier:\n', 'dim')
    colour_print('  [1]  Low-sec   — Corporate Server  (easy)', 'cyan')
    colour_print('  [2]  Mid-sec   — Bank Network       (medium)', 'yellow')
    colour_print('  [3]  High-sec  — Military Firewall  (hard)', 'red')
    print()
    raw = safe_input('\033[92m  > \033[0m').strip()

    difficulty = {'1': 1, '2': 2, '3': 3}.get(raw, 1)

    name = safe_input('\033[96m  Enter your hacker alias: \033[0m').strip()
    if not name:
        name = 'Ghost'
    player = Player(name)
    print()

    mission = FreelanceMission(player, difficulty=difficulty)
    mission.start()
    press_enter('  [ READY TO CONNECT? ] Press ENTER...')

    result = mission.run()

    mode_tag = f'freelance-{difficulty}'
    record_run(player, mode=mode_tag, missions_done=0, ending='')

    if result:
        _offer_leaderboard_entry(player, mode=mode_tag, missions_done=0)
    else:
        colour_print('\n  Contract failed. Credits withheld.\n', 'red')
        pause(2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    show_logo()

    while True:
        colour_print('\n  [ NEURAL LINK TERMINAL  v0.2.0 ]\n', 'green')
        choice = show_main_menu()

        if choice == '1':
            player = start_new_game()
            run_missions(player)

        elif choice == '2':
            player, mission_id = load_existing_game()
            if player:
                run_missions(player, mission_id)

        elif choice == '3':
            run_freelance_mode()

        elif choice == '4':
            display_leaderboard()

        elif choice == '5':
            display_career()

        elif choice == '6':
            print()
            slow_print('  Terminating neural link...', delay=0.04, colour='dim')
            slow_print('  Stay ghost.\n',              delay=0.04, colour='dim')
            sys.exit(0)

        else:
            colour_print('  [!] Invalid option.\n', 'red')


if __name__ == '__main__':
    main()
