# Record Label - A Worker Placement Game

A multiplayer worker placement board game with a music industry theme, inspired by Lords of Waterdeep. Players run competing record labels, placing workers to collect musicians, complete contracts, construct buildings, and play intrigue cards.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended for environment management)

## Setup

```bash
uv venv
uv pip install -e ".[dev]"
```

## Running

Start the server:

```bash
python -m server.main
```

In separate terminals, launch one or more clients:

```bash
python -m client.main
```

### Client options

```
--server URL    Server WebSocket URL (default: ws://localhost:8765)
--fullscreen    Launch in fullscreen mode
--name NAME     Pre-fill your display name
```

### Server options

```
--host HOST       Bind address (default: 0.0.0.0)
--port PORT       Port (default: 8765)
--config DIR      Config directory (default: config/)
--log-level LEVEL Logging level (default: INFO)
```

## How to Play

1. One player creates a game and shares the game code.
2. Other players join using the code (2-5 players).
3. Over 8 rounds, place workers on action spaces to collect musicians (guitarists, bass players, drummers, singers) and coins.
4. Spend resources to complete contracts for victory points.
5. Use Backstage to play intrigue cards and reassign workers for extra actions.
6. Construct buildings to create new action spaces and earn owner bonuses.
7. At game end, Producer card bonuses are revealed. Highest VP wins.

## Project Structure

```
client/          Desktop client (Arcade)
server/          Headless WebSocket server
shared/          Shared models and constants (Pydantic)
config/          Game data (contracts, buildings, intrigue cards, etc.)
tests/           Test suite
specs/           Feature specifications
```

## Tests

```bash
pytest
```
