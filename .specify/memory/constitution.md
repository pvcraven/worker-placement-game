<!--
  Sync Impact Report
  Version change: 1.0.0 → 2.0.0
  Modified principles: None
  Added sections:
    - Principle 6: Server-Authoritative Message Protocol
    - Principle 7: Config-Driven Game Content
    - Principle 8: Pending State for Deferred Actions
    - Principle 9: Cancel/Unwind Reversibility
    - Principle 10: Post-Action Turn Flow
    - Section: Project Structure (expanded)
  Removed sections: None
  Templates requiring updates:
    ✅ plan-template.md — no changes needed (dynamic Constitution Check)
    ✅ spec-template.md — no changes needed (generic)
    ✅ tasks-template.md — no changes needed (generic)
  Follow-up TODOs: None
-->

# Record Label Constitution

## Core Principles

### I. Arcade Rendering Standards

All client-side rendering MUST use `arcade.Text` for text display
and `ShapeElementList` for shape-based graphics.

- Code MUST NOT call `arcade.draw_text()` or any primitive draw
  functions (`draw_rectangle_filled`, `draw_circle_filled`, etc.).
- All text elements MUST be created as `arcade.Text` instances,
  cached and reused across frames.
- All geometric shapes MUST be composed into `ShapeElementList`
  objects for batch rendering.
- Sprites and sprite lists remain the preferred approach for
  image-based rendering.

**Rationale**: Primitive draw calls rebuild GPU state every frame,
causing poor performance. `arcade.Text` and `ShapeElementList`
cache GPU buffers and render efficiently at scale.

### II. Pydantic Data Modeling

All structured data that crosses boundaries (network, config,
persistence) MUST be defined as Pydantic models.

- Raw `dict` usage MUST be replaced with typed Pydantic models
  when the dict carries more than two keys or is passed between
  modules.
- Shared models between client and server MUST live in the
  `shared/` package.
- Config files (JSON) MUST be loaded and validated through
  Pydantic models.
- Network messages MUST be serialized/deserialized via Pydantic's
  `model_dump()` / `model_validate()`.

**Rationale**: Pydantic provides runtime validation, clear schemas,
and IDE-friendly type hints — eliminating a class of bugs caused by
untyped dicts and ad-hoc serialization.

### III. Client-Server Separation

The game MUST maintain strict separation between client (Arcade UI),
server (game engine), and shared (models/messages).

- Game rules and state mutations MUST live exclusively in
  `server/`.
- The client MUST NOT modify game state directly; it sends
  messages and renders state received from the server.
- All data structures shared between client and server MUST
  reside in `shared/`.
- The server MUST be runnable headlessly without any Arcade
  dependency.

**Rationale**: Clean separation enables headless testing, prevents
UI logic from corrupting game state, and keeps the shared protocol
as the single source of truth.

### IV. Test-Driven Game Logic

Server-side game logic MUST have automated test coverage.

- New game rules, state transitions, and validation logic MUST
  have corresponding pytest tests.
- Tests MUST run via `pytest` from the project root.
- Tests MUST NOT depend on the Arcade library or a running
  client.
- Code quality MUST be verified with `ruff check .`.

**Rationale**: Game logic bugs are hard to reproduce manually.
Automated tests catch rule violations and state corruption early.

### V. Simplicity First

Implementations MUST favor the simplest solution that meets
the current requirement.

- YAGNI: do not build abstractions for hypothetical future
  features.
- Prefer flat, readable code over clever patterns.
- New dependencies MUST be justified by a concrete need, not
  speculative convenience.
- In-memory game state on the server is sufficient until a
  persistence requirement is specified.

**Rationale**: Premature abstraction increases cognitive load and
maintenance cost without delivering user-facing value.

### VI. Server-Authoritative Message Protocol

Every game interaction follows a Request → Server Handler →
Broadcast/Send Response triad.

- Each interaction MUST have a paired Request and Response type
  in `shared/messages.py`, discriminated on the `action` field.
- State-changing responses MUST be broadcast to all players via
  `broadcast_to_game()`.
- Player-specific prompts (choices, completions) MUST be sent
  only to the relevant player via `send_to_player()`.
- Broadcast responses MUST include `next_player_id` so clients
  know whose turn it is.
- The client's local `game_state` dict is a render cache only.
  On reconnect, `StateSyncResponse` replaces it entirely.

**Rationale**: A single message protocol prevents client/server
state divergence. Broadcast vs. targeted sending keeps bandwidth
low and prevents UI leaking private info (hands, decks).

### VII. Config-Driven Game Content

Game content (buildings, contracts, intrigue cards, board layout)
MUST be data-driven through JSON config files, never hard-coded.

- New game content MUST be added as JSON entries in `config/`
  with corresponding Pydantic model fields in `shared/card_models.py`.
- Server logic MUST branch on model field values, not on
  hard-coded IDs (e.g., check `card.reward_draw_intrigue > 0`,
  not `card.id == "contract_funk_005"`).
- New abilities or reward types MUST be expressed as new fields
  on existing models (e.g., `reward_use_occupied_building: bool`,
  `visitor_reward_special: str`), not as new code branches per card.
- Action space types (`permanent`, `building`, `garage`, `castle`,
  `realtor`, `backstage`) determine the reward and interaction path.
  New types MUST be documented in the ActionSpace model.

**Rationale**: Data-driven design means new content (cards,
buildings, quests) can be added by editing JSON + adding a model
field, without touching core game logic. This has scaled from 5
buildings to 20+ without architectural changes.

### VIII. Pending State for Deferred Actions

When a game action requires additional player input before
resolving, the server MUST store intent in a `pending_*` field
on `GameState`.

- Pending fields MUST follow the naming convention
  `pending_<action>: dict | None` (e.g., `pending_resource_choice`,
  `pending_intrigue_target`, `pending_placement`).
- The server MUST send a prompt response to the player, then
  return (not block).
- The player's subsequent request handler MUST read and clear
  the pending field.
- If the player cancels, the pending field MUST be cleared and
  any side effects reversed.

**Rationale**: The server is stateless between messages. Pending
fields are the explicit state machine that tracks where each
multi-step interaction is in its lifecycle. Without them,
the server cannot distinguish "waiting for quest choice" from
"waiting for intrigue target."

### IX. Cancel/Unwind Reversibility

Any placement or action that pauses for player input MUST be
fully reversible if the player cancels.

- The `pending_placement` dict MUST capture `space_id`,
  `granted_resources`, `granted_vp`, `owner_bonus_info`,
  `trigger_bonuses`, and `accumulated_stock_consumed` at the
  moment of placement.
- Cancel handlers MUST use `_unwind_placement()` to reverse all
  side effects rather than re-deriving what to undo.
- Cancel handlers MUST NOT search action spaces to find the
  placed worker — the `space_id` is in `pending_placement`.

**Rationale**: Searching for which space to free caused a real
bug where cancelling freed the wrong building. Capturing the
exact placement data at placement time makes cancel deterministic
and correct.

### X. Post-Action Turn Flow

After every action that resolves a player's turn, the server
MUST follow the standard turn-advance sequence.

- Call `_check_quest_completion()` to prompt for completable
  quests before advancing.
- Call `_advance_turn()` to move `current_player_index` to
  the next player, or transition to reassignment/round-end
  when all workers are placed.
- Clear `pending_placement` in `_advance_turn()` as a safety
  net.
- After resource grants, call `_evaluate_resource_triggers()`
  and broadcast any trigger bonuses to the client.

**Rationale**: Consistent post-action flow prevents turns from
getting stuck. Every spec since 006 relies on this sequence;
skipping any step causes the game to hang or skip quest
completion opportunities.

## Technology Stack

- **Language**: Python 3.12+
- **Client UI**: Arcade library (local source at
  `C:\Users\PaCra\Projects\arcade`)
- **Networking**: websockets (async, JSON messages)
- **Data Validation**: Pydantic v2
- **Testing**: pytest + ruff
- **Environment**: uv for dependency management
- **Config Format**: JSON files in `config/`

## Project Structure

```
client/                    # Arcade UI (render-only, no game logic)
  views/                   # View classes (menu, lobby, game)
  ui/                      # Reusable UI components (board renderer, panels)
  assets/                  # Images, sounds, card art
  network_client.py        # Threaded WebSocket client
  game_window.py           # Main Arcade window
server/                    # Authoritative game engine
  game_engine.py           # All game logic handlers
  lobby.py                 # Game creation, joining, start
  network.py               # WebSocket server + dispatch
  models/                  # Server-only Pydantic models (game state, config)
shared/                    # Shared between client and server
  messages.py              # All Request/Response message types
  card_models.py           # ContractCard, IntrigueCard, BuildingTile, etc.
  constants.py             # Enums (GamePhase, Genre), constants
config/                    # JSON game content (never import from code)
  board.json               # Permanent action spaces, building lots
  buildings.json           # Building tiles with rewards/specials
  contracts.json           # Quest/contract cards
  intrigue.json            # Intrigue cards
  producers.json           # End-game producer scoring cards
  game_rules.json          # Round count, timeouts, worker counts
tests/                     # pytest tests (server logic only)
specs/                     # Feature specifications and plans
```

## Development Workflow

- Run tests and linting before committing: `cd src && pytest &&
  ruff check .`
- Feature work happens on named branches
  (`###-feature-name`).
- Specs live in `specs/###-feature-name/`.
- Commit after each logical unit of work.
- Server and client are started in separate terminals for
  manual testing.

## Governance

This constitution is the authoritative guide for all development
decisions in the Record Label project. When a proposed change
conflicts with a principle above, the principle takes precedence
unless the constitution is formally amended.

**Amendment procedure**:

1. Propose the change with rationale.
2. Update this document with the new or modified principle.
3. Increment the version per semantic versioning:
   - MAJOR: principle removed or redefined incompatibly.
   - MINOR: new principle or material expansion.
   - PATCH: wording clarification or typo fix.
4. Update `LAST_AMENDED_DATE`.
5. Verify consistency with templates in `.specify/templates/`.

**Compliance**: All feature specs, plans, and task lists MUST
be reviewed against this constitution before implementation
begins.

**Version**: 2.0.0 | **Ratified**: 2026-04-18 | **Last Amended**: 2026-04-29
