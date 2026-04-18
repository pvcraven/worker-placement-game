<!--
  Sync Impact Report
  Version change: 0.0.0 (template) → 1.0.0
  Modified principles: N/A (initial population)
  Added sections:
    - Principle 1: Arcade Rendering Standards
    - Principle 2: Pydantic Data Modeling
    - Principle 3: Client-Server Separation
    - Principle 4: Test-Driven Game Logic
    - Principle 5: Simplicity First
    - Section: Technology Stack
    - Section: Development Workflow
    - Governance
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

## Technology Stack

- **Language**: Python 3.12+
- **Client UI**: Arcade library (local source at
  `C:\Users\PaCra\Projects\arcade`)
- **Networking**: websockets (async, JSON messages)
- **Data Validation**: Pydantic v2
- **Testing**: pytest + ruff
- **Environment**: uv for dependency management
- **Config Format**: JSON files in `config/`

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

**Version**: 1.0.0 | **Ratified**: 2026-04-18 | **Last Amended**: 2026-04-18
