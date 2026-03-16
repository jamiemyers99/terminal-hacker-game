[![Header](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,12,20&height=200&section=header&text=TERMINAL%20HACKER&fontSize=52&fontColor=00FF41&animation=fadeIn&fontAlignY=38&desc=//%20NEURAL%20INTRUSION%20SYSTEM%20%C2%B7%20v0.2.0%20%E2%80%94%20The%20ghost%20in%20the%20machine%20is%20you.&descSize=15&descColor=00FFFF&descAlignY=60)](https://github.com/jamiemyers99/terminal-hacker-game)

<div align="center">

```
████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║
   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
```

[![Tests](https://github.com/jamiemyers99/terminal-hacker-game/actions/workflows/test.yml/badge.svg)](https://github.com/jamiemyers99/terminal-hacker-game/actions/workflows/test.yml)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00FF41?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-00FFFF?style=flat-square)
![Status](https://img.shields.io/badge/Status-Playable-00FF41?style=flat-square)
![Version](https://img.shields.io/badge/Version-0.2.0-1e2530?style=flat-square)
![No Dependencies](https://img.shields.io/badge/Dependencies-stdlib%20only-00FFFF?style=flat-square)

**A text-based terminal hacking simulation built entirely in Python.**
Navigate a cyberpunk city's criminal underworld through four escalating missions —
crack passwords, decode cipher sequences, and navigate firewall mazes
before the trace meter burns you.

</div>

---

## `> cat features.txt`

- 🔐 **Three distinct mini-games** — password cracker, sequence decoder (breach protocol), and a randomly-generated firewall maze
- 📡 **Trace meter** — every mistake inches you toward detection; hit 100% and the system locks you out
- 🌿 **Branching narrative** — four story missions with unique flavour text, escalating difficulty, and a final boss with two separate endings
- 🛠️ **Tool system** — collect `port_scanner`, `vpn_shield`, and `root_kit` across missions; each carries forward and changes how future missions play out
- ⚡ **Freelance contracts** — procedurally generated one-shot jobs with randomised clients, targets, and complications across three difficulty tiers
- 🏆 **Local leaderboard** — top-10 high scores persisted to `data/leaderboard.json`; submit your alias after any run
- 📊 **Career tracker** — cumulative stats (story runs, freelance contracts, lifetime credits, endings) across all sessions
- 💾 **Save / load** — JSON-based game state persists your progress between sessions
- ⌨️ **Typewriter output** — all narrative text prints character-by-character; press Enter or Space to skip
- 🎨 **Cyberpunk aesthetic** — green-on-black ANSI colour, Unicode box-drawing art, and per-system ASCII banners
- 🌐 **Cross-platform** — pure stdlib; optional `colorama` for Windows legacy terminal support

---

## `> ./demo.sh`

> 💡 Record a gameplay session with [Asciinema](https://asciinema.org/) or [Terminalizer](https://www.terminalizer.com/) and embed a GIF here.

```
  ╔══════════════════════════════════════════════════════════╗
  ║         NEURAL INTRUSION SYSTEM  ·  v0.2.0              ║
  ╚══════════════════════════════════════════════════════════╝

  [ NEURAL LINK TERMINAL  v0.2.0 ]

  ┌──────────────────────────────────┐
  │   [1]  New Game                  │
  │   [2]  Load Game                 │
  │   [3]  Freelance Run             │
  │   [4]  Leaderboard               │
  │   [5]  Career                    │
  │   [6]  Quit                      │
  └──────────────────────────────────┘

  > _
```

---

## `> git clone && run`

```bash
# Clone the repository
git clone https://github.com/jamiemyers99/terminal-hacker-game
cd terminal-hacker-game

# No install required — pure Python 3 stdlib
python main.py

# Optional: install colorama for reliable colour on Windows legacy terminals
pip install colorama
python main.py
```

> **Requirements:** Python 3.8 or later. No third-party packages required.

---

## `> pytest tests/ -v`

```bash
cd terminal-hacker-game
python -m pytest tests/ -v
```

| Module | Coverage |
|--------|---------|
| `engine/player.py` | Tool management, trace mechanics, level cap, serialisation round-trip |
| `engine/game_state.py` | Save / load / delete with file isolation, corrupt JSON handling |
| `engine/leaderboard.py` | Entry storage, sort order, MAX_ENTRIES cap, `is_high_score` logic |
| `engine/career.py` | All stat fields, ending tracking, back-fill of missing keys |
| `minigames/` | Grid dimensions, solvable-target constraint proof, maze BFS connectivity |
| `missions/freelance.py` | Briefing content/variation, system routing per difficulty |

> Tests run automatically on every push via GitHub Actions across Python 3.8, 3.10, and 3.12.

---

## `> man how-to-play`

### Objective

You are a freelance hacker navigating a corrupt cyberpunk city. Work through four missions — each connecting you to a progressively harder system. Complete all four to expose the conspiracy at the heart of **PROMETHEUS**.

### The Trace Meter

```
  TRACE: [████████░░░░░░░░░░░░] 40%
```

The trace bar fills every time you make a mistake. Reach **100%** and the target system locks you out — mission failed. The bar resets after each successfully completed mission, but **not** between the three stages of the final boss.

---

### 🔑 Mini-Game 1 — Password Cracker

Guess a hidden password within a limited number of attempts.

| Difficulty | Word Pool | Attempts | Trace Per Wrong Guess |
|------------|-----------|----------|-----------------------|
| Easy | 5-letter common words | 8 | +5 |
| Medium | 6-letter technical words | 6 | +10 |
| Hard | 8-letter hacker terms | 4 | +15 |

**Feedback:** After each wrong guess you receive Wordle-style feedback — how many letters are in the correct position, and how many are in the word but misplaced.

| Input | Effect |
|-------|--------|
| `hint` | Reveals one random letter — costs extra trace |
| `t` | Opens the toolkit overlay — does not use a guess |

---

### 🔢 Mini-Game 2 — Sequence Decoder

A breach-protocol puzzle inspired by *Cyberpunk 2077*. Match a target sequence of hex values by navigating the grid under an alternating row/column constraint.

```
  TARGET : [ 7C ]  [ 1A ]  [ FF ]
  BUFFER : [ 7C ]  [ __ ]  [ __ ]

  MOVES LEFT: 6

       0     1     2     3
     ┌─────┬─────┬─────┬─────┐
  0  │ 7C  │ E4  │ 1A  │ FF  │  ← active row
     ├─────┼─────┼─────┼─────┤
  1  │ 2B  │ 7C  │ 3D  │ 1A  │
     ├─────┼─────┼─────┼─────┤
  2  │ FF  │ 2B  │ E4  │ 7C  │
     ├─────┼─────┼─────┼─────┤
  3  │ 1A  │ FF  │ 7C  │ 2B  │
     └─────┴─────┴─────┴─────┘
```

**Rules:** Even turns pick any column from the highlighted row. Odd turns pick any row from the highlighted column. The target sequence is always achievable — plan your path before committing.

---

### 🌀 Mini-Game 3 — Firewall Maze

Navigate from the top-left `()` to the exit `><` through a randomly generated maze. Trace increases every N steps.

```
  ██████████████████████
  ██()      ██    ██████
  ██  ██████  ██  ██  ██
  ██      ██      ██  ██
  ████  ████  ████████  ██
  ██              ><  ██
  ██████████████████████
```

| Key | Action |
|-----|--------|
| `W` / `↑` | Move up |
| `S` / `↓` | Move down |
| `A` / `←` | Move left |
| `D` / `→` | Move right |
| `I` | Open toolkit |
| `Q` | Abort connection |

> The maze is regenerated randomly every run — no two playthroughs are the same.

---

### 🛠️ Tools

| Tool | Acquired | Effect |
|------|----------|--------|
| `port_scanner` | Mission 1 reward | Passive: grants a -15 trace buffer at the start of Mission 2 |
| `vpn_shield` | Mission 2 reward | Single-use: halves all trace gain during Mission 3 |
| `root_kit` | Mission 3 reward | Single-use: auto-solves one mini-game stage in Mission 4 |

> Press `T` at any text input prompt during a mission to view your toolkit.

---

### 📋 Missions

| # | Title | System | Mini-Game | Difficulty |
|---|-------|--------|-----------|------------|
| 1 | The Leak | NexusCorp Internal | Password Cracker | ★ |
| 2 | Follow the Money | Iron Vault Financial | Sequence Decoder | ★★ |
| 3 | Ghost Protocol | Daedalus Defence Network | Firewall Maze | ★★★ |
| 4 | Zero Day *(boss)* | PROMETHEUS AI Core | All three in order | ★★★★★ |

> **Mission 4** runs all three mini-games back-to-back with no trace reset between stages. On success, a final choice determines one of two distinct endings.

---

## `> tree .`

```
terminal-hacker-game/
│
├── main.py                   # Entry point — title screen, menu, mission runner
│
├── engine/
│   ├── display.py            # slow_print, colour_print, print_banner, status bar
│   ├── player.py             # Player class — level, tools, trace, credits
│   ├── game_state.py         # save_game / load_game / delete_save (JSON)
│   ├── leaderboard.py        # Top-10 high scores (data/leaderboard.json)
│   ├── career.py             # Cross-session career stats (data/career.json)
│   ├── sound.py              # play_sound — winsound / afplay / silent
│   └── utils.py              # safe_input, game_input, pause, press_enter
│
├── minigames/
│   ├── password_cracker.py   # Wordlist-based guessing with Wordle feedback
│   ├── sequence_decoder.py   # Breach protocol (alternating row/col selection)
│   └── firewall_maze.py      # DFS-generated maze, WASD navigation
│
├── systems/
│   ├── base_system.py        # BaseSystem — connect → minigame → success/bust
│   ├── corporate_server.py   # NexusCorp   (security level 1)
│   ├── bank_network.py       # Iron Vault  (security level 2)
│   ├── military_firewall.py  # Daedalus    (security level 3)
│   └── ai_core.py            # PROMETHEUS  (security level 5, boss)
│
├── missions/
│   ├── mission_base.py       # MissionBase — start / run / complete / fail
│   ├── the_leak.py           # Mission 1 — tutorial
│   ├── follow_the_money.py   # Mission 2
│   ├── ghost_protocol.py     # Mission 3
│   ├── zero_day.py           # Mission 4 — final boss, two endings
│   └── freelance.py          # Procedural one-shot contracts (3 difficulty tiers)
│
├── assets/
│   └── ascii_art.py          # All ASCII art strings (logo, banners, outcomes)
│
├── data/
│   ├── wordlists.json        # easy / medium / hard password wordlists
│   ├── save.json             # Auto-generated (gitignored)
│   ├── leaderboard.json      # Auto-generated (gitignored)
│   └── career.json           # Auto-generated (gitignored)
│
├── tests/
│   ├── test_player.py
│   ├── test_game_state.py
│   ├── test_leaderboard.py
│   ├── test_career.py
│   ├── test_minigames.py
│   └── test_freelance.py
│
├── .github/workflows/test.yml
├── .gitignore
├── LICENSE
└── README.md
```

---

## `> cat roadmap.md`

- [x] High score leaderboard — saved locally, submit alias after any run *(v0.2.0)*
- [x] Random mission generator — procedurally generated freelance contracts *(v0.2.0)*
- [x] Career tracker — cumulative stats with reputation ranking *(v0.2.0)*
- [ ] Multiplayer — one player as the hacker, one controlling the defence systems
- [ ] More mini-games — social engineering prompts, SQL injection puzzles, port enumeration
- [ ] Web version — browser-playable port via [Brython](https://brython.info/) or [Transcrypt](https://transcrypt.org/)
- [ ] Replay system — record and share a run using Asciinema

---

## `> git contribute`

Contributions, issues and feature requests are welcome. Feel free to open an issue or submit a pull request.

```bash
git checkout -b feature/my-feature
git commit -m 'Add my feature'
git push origin feature/my-feature
# Open a pull request on GitHub
```

---

<div align="center">

[![Footer](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,12,20&height=100&section=footer&animation=fadeIn)](https://github.com/jamiemyers99/terminal-hacker-game)

![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=jamiemyers99.terminal-hacker-game)

`// MIT License · © 2026 Jamie Myers · Sligo, Ireland`

</div>