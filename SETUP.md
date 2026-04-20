# Tester Setup Guide

## Prerequisites

1. **Python 3.12+** — Download from https://www.python.org
   - During installation, check **"Add Python to PATH"**
2. **Git** — Download from https://git-scm.com

## First-Time Setup

Open a terminal (Command Prompt or PowerShell) and run:

```
git clone https://github.com/pvcraven/Worker-Placement-Game.git
cd Worker-Placement-Game
play.bat
```

## Playing After Setup

Open a terminal in the `Worker-Placement-Game` folder and run:

```
play.bat
```

This will automatically pull the latest code, install any new dependencies, start the server, and launch the game.

## Multiplayer (LAN)

One player hosts by running `play.bat` as usual. Other players on the same network connect by running:

```
python -m client.main --server ws://<host-ip>:8765
```

Replace `<host-ip>` with the host's local IP address (e.g., `192.168.1.42`).

## Troubleshooting

- **"Python not found"** — Reinstall Python with "Add to PATH" checked, then restart your terminal.
- **Game won't update** — If you've accidentally edited files, run `git checkout .` then `play.bat` again.
- **Port already in use** — The launcher tries to clean up old servers automatically. If it fails, restart your computer or manually kill the process on port 8765.
