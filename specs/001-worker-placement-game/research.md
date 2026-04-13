# Phase 0 Research: Multiplayer Worker Placement Game

**Branch**: `001-worker-placement-game` | **Date**: 2026-04-13 | **Plan**: [plan.md](plan.md)

## Technology Decisions

### 1. Graphics Library: Arcade

**Decision**: Use Python Arcade library for the graphical client.

**Rationale**: Arcade is a modern Python 2D game library built on Pyglet/OpenGL that provides:
- Hardware-accelerated 2D rendering suitable for board game UIs
- Built-in window resize/fullscreen support via `Window.on_resize()`
- View system (`arcade.View`) for clean screen management (menu, lobby, game, results)
- Sprite-based rendering for cards, tokens, and board elements
- Text rendering with custom fonts
- Mouse/keyboard input handling
- Cross-platform desktop support (Windows, macOS, Linux)

**Alternatives Considered**:
- **Pygame**: More established but lower-level API, no built-in View system, manual OpenGL for scaling
- **Pyglet**: Arcade is built on Pyglet; using Arcade directly provides higher-level abstractions
- **Kivy**: Better for touch UIs but more complex for traditional desktop board games
- **Web-based (Flask/FastAPI + JS)**: Would simplify networking but adds frontend language split and browser dependency

**Key Arcade Patterns**:
- Use `arcade.View` subclasses for each screen (MenuView, LobbyView, GameView, ResultsView)
- Use `arcade.Window` with `resizable=True` for responsive layout
- Use `arcade.SpriteList` for efficient batch rendering of cards and tokens
- Use `arcade.gui.UIManager` for buttons, text inputs, and dialog boxes
- Schedule network polling via `arcade.schedule()` or use a background thread with a queue

### 2. Networking: websockets Library

**Decision**: Use the `websockets` Python library for client-server communication.

**Rationale**: The `websockets` library provides:
- Pure Python async WebSocket implementation
- Clean asyncio integration for the server
- Automatic ping/pong keepalive for connection health
- Built-in reconnection patterns
- Lightweight — no external server infrastructure needed
- Full-duplex communication for server-push state updates

**Alternatives Considered**:
- **Socket.IO (python-socketio)**: Adds rooms/namespaces but brings unnecessary HTTP overhead and JS-oriented design
- **Raw TCP sockets**: Lower-level, requires custom framing protocol
- **gRPC**: Overkill for turn-based game; adds protobuf compilation step
- **MQTT**: Pub/sub model doesn't align well with request/response game actions

**Architecture**:
- Server runs an `asyncio` event loop with `websockets.serve()`
- Each client connection gets a handler coroutine managing that player's session
- Server broadcasts state updates to all clients in a game session
- Client runs WebSocket in a background thread (Arcade's main loop is synchronous), communicating with the game view via a thread-safe queue

### 3. Data Validation: Pydantic

**Decision**: Use Pydantic v2 for all structured data validation and serialization.

**Rationale**: Pydantic provides:
- Type-safe model definitions with automatic validation
- JSON serialization/deserialization via `.model_dump_json()` / `.model_validate_json()`
- Discriminated unions for polymorphic message types (different message kinds over WebSocket)
- Config file schema validation on server startup
- Clear error messages for malformed data
- IDE support via type annotations

**Alternatives Considered**:
- **dataclasses + manual validation**: More boilerplate, no built-in JSON schema support
- **attrs + cattrs**: Good alternative but less JSON-native than Pydantic
- **marshmallow**: Schema-first approach; more verbose for this use case
- **Plain dicts**: No validation, error-prone, poor IDE support

**Usage Plan**:
- **Shared models** (`shared/`): Network message schemas (requests/responses), card attribute models
- **Server models** (`server/models/`): Full game state, player state, config file schemas
- **Config validation**: Pydantic models for each JSON config file (contracts, intrigue, buildings, producers, board, game_rules)
- **Discriminated unions**: `Literal` type field on messages for `action` routing (e.g., `{"action": "place_worker", ...}`)

### 4. Server Architecture: Headless asyncio

**Decision**: Standalone headless Python server using `asyncio` as the event loop.

**Rationale**:
- No web framework needed — the server only handles WebSocket connections
- `asyncio` provides cooperative multitasking suitable for turn-based game management
- Single-process, multi-session — each game session is a set of coroutines
- Simple deployment: `python -m server.main` starts the server

**Alternatives Considered**:
- **FastAPI + WebSocket**: Adds HTTP routing overhead; useful only if REST endpoints were also needed
- **Twisted**: Mature but callback-heavy; asyncio is the modern Python standard
- **Multi-process**: Unnecessary for 10 concurrent sessions of a turn-based game

**Session Management**:
- A `SessionManager` maps game codes to `GameSession` objects
- Each `GameSession` holds the authoritative `GameState` and manages connected players
- Disconnected players are tracked with a reconnection window (30-minute timeout)
- Turn timeouts (60s default) auto-skip disconnected/idle players

### 5. Testing: pytest + pytest-asyncio

**Decision**: Use pytest with pytest-asyncio for all testing.

**Rationale**:
- pytest is the standard Python testing framework
- pytest-asyncio enables testing async WebSocket server code
- Fixtures can provide pre-configured game states for unit tests
- Parametrize decorators enable testing many card/config combinations efficiently

**Test Structure**:
- `tests/unit/`: Game engine logic, state management, config loading, model validation
- `tests/integration/`: Lobby flow, full game flow, reconnection, reassignment phase
- `tests/contract/`: Message schema compatibility, config schema validation

## Domain Research

### Worker Placement Mechanics (Lords of Waterdeep Reference)

**Turn Structure**: Players take turns placing one worker at a time in clockwise order. When all workers are placed, the round ends. The game runs for 8 rounds.

**Resource Economy**: Four musician types + Coins. Resources are spent to complete Contracts (quests). Economy is zero-sum with the board — players gain resources only from action spaces.

**The Garage (Harbor) Mechanic**: Critical two-phase mechanic:
1. **Placement Phase**: Worker goes to Garage slot (1/2/3), player plays intrigue card immediately
2. **Reassignment Phase**: After ALL workers placed, Garage workers reassign in slot order to any unoccupied space (except Garage). This is a "double action" — the most powerful mechanic in the game.

**First-Player Marker**: Castle Waterdeep grants first-player marker + 1 intrigue card. First player advantage is significant in worker placement games since desirable spaces fill up.

**Building Construction**: Buildings create new action spaces. The owner gets a kickback (bonus) when other players use it. This creates a long-term investment strategy.

**Producer Cards (Lord Cards)**: Secret scoring objectives revealed at game end. ~11 different producers, each favoring 2 genres. Typical bonus: +4 VP per completed contract of the favored genres.

### Responsive UI Scaling Strategy

**Approach**: Use a virtual coordinate system with proportional scaling.
- Define a "design resolution" (e.g., 1920x1080) for layout
- Scale all rendering by `min(actual_width/design_width, actual_height/design_height)`
- Board elements use proportional positioning (percentage-based)
- Minimum window size enforced (e.g., 1024x768) — below this, show a "window too small" overlay
- Font sizes scale with window but have minimums for readability

### Config File Design

**Format**: JSON files with Pydantic schema validation on load.

**Validation Strategy** (per FR-028):
- **Hard errors**: Missing required fields, wrong types, duplicate IDs, invalid references
- **Warnings**: Zero-cost contracts, unusually high VP rewards (>20), empty descriptive text
- **Flexible**: Extra fields ignored (forward compatibility for modding)

## Resolved Unknowns

All Technical Context items were specified by the user. No NEEDS CLARIFICATION items remain. Key decisions that could have been ambiguous:

| Item | Resolution | Source |
|------|-----------|--------|
| Graphics library | Arcade | User specification |
| Networking protocol | WebSocket (JSON) | User specification |
| Data validation | Pydantic | User specification |
| Server architecture | Headless Python asyncio | User specification |
| Client architecture | Arcade desktop app | User specification + spec |
| Testing framework | pytest + pytest-asyncio | Plan decision (standard choice) |
| Config format | JSON with Pydantic validation | User specification + FR-026/028 |
| Shared code strategy | `shared/` package imported by both server and client | Plan decision |
