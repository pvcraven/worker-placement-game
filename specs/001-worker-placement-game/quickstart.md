# Quickstart Guide: Multiplayer Worker Placement Game

**Branch**: `001-worker-placement-game` | **Date**: 2026-04-13

## Prerequisites

- Python 3.12+
- pip (or uv/poetry)

## Setup

```bash
# Clone and enter the project
cd "Worker Placement Game"

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install arcade websockets pydantic pytest pytest-asyncio
```

## Project Structure

```
server/          # Headless game server (asyncio + websockets)
client/          # Arcade graphical client
shared/          # Pydantic models shared by both server and client
config/          # JSON game content (contracts, intrigue, buildings, etc.)
tests/           # Unit, integration, and contract tests
```

## Running the Server

```bash
python -m server.main
```

The server starts on `ws://localhost:8765` by default. It accepts WebSocket connections and manages game lobbies and sessions.

**Command-line options** (planned):
- `--host 0.0.0.0` — bind to all interfaces (LAN play)
- `--port 8765` — WebSocket port
- `--config config/` — path to config directory

## Running the Client

```bash
python -m client.main
```

The client opens an Arcade window with the main menu. From there:
1. **Create Game** — starts a new lobby, displays a game code
2. **Join Game** — enter a game code to join an existing lobby

**Command-line options** (planned):
- `--server ws://localhost:8765` — server address
- `--fullscreen` — launch in fullscreen mode
- `--name "My Label"` — pre-fill display name

## Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Contract/schema tests only
pytest tests/contract/

# With verbose output
pytest -v

# Specific test file
pytest tests/unit/test_game_engine.py
```

## Config Files

Game content lives in `config/`. All files are JSON and validated by Pydantic on server startup.

| File | Contents | Approximate Count |
|------|----------|-------------------|
| `contracts.json` | Contract (quest) cards | 60 cards |
| `intrigue.json` | Intrigue cards | 50 cards |
| `buildings.json` | Building tiles | 24 tiles |
| `producers.json` | Producer cards | ~11 cards |
| `board.json` | Permanent action spaces and building lots | 9 spaces |
| `game_rules.json` | Round count, worker scaling, timeouts | — |

To modify game balance, edit these JSON files directly. The server validates structure on startup and warns about suspicious values (e.g., zero-cost contracts).

### Example Contract Card

```json
{
  "id": "contract_jazz_001",
  "name": "Midnight Jazz Ensemble",
  "description": "Assemble a smooth jazz combo for the downtown club circuit.",
  "genre": "jazz",
  "cost": {
    "guitarists": 1,
    "bass_players": 1,
    "drummers": 1,
    "singers": 0,
    "coins": 0
  },
  "victory_points": 4,
  "bonus_resources": {
    "guitarists": 0,
    "bass_players": 0,
    "drummers": 0,
    "singers": 0,
    "coins": 2
  },
  "is_plot_quest": false,
  "ongoing_benefit_description": null
}
```

## Development Workflow

1. **Server-first**: Implement game logic and state management in `server/`
2. **Shared models**: Define message types in `shared/messages.py` — both server and client import these
3. **Client views**: Build Arcade views in `client/views/` consuming shared message types
4. **Config files**: Populate `config/` with game content; run server to validate
5. **Tests**: Write tests alongside implementation; run `pytest` continuously

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `arcade` | >=3.0 | Graphics, window management, UI |
| `websockets` | >=12.0 | Async WebSocket server and client |
| `pydantic` | >=2.0 | Data validation, serialization, config schemas |
| `pytest` | >=8.0 | Test framework |
| `pytest-asyncio` | >=0.23 | Async test support |
