# Research: Informational Dialog System

## Decision 1: Timer Mechanism

**Decision**: Use `on_update` delta-time accumulator for auto-dismiss timing.

**Rationale**: The game view already has an `on_update(delta_time)` method that runs every frame. Accumulating elapsed time and checking against the duration threshold is the simplest possible approach — no callbacks, no arcade scheduling, no cleanup needed.

**Alternatives considered**:
- `arcade.schedule()` — Adds callback lifecycle management (must unschedule on view change). Unnecessary complexity for a simple countdown.
- `asyncio.sleep()` — Would block or require async plumbing. Incompatible with Arcade's synchronous draw loop.

## Decision 2: Dialog Queue vs. Replace

**Decision**: Queue dialogs — if a new dialog is triggered while one is active, it waits in a FIFO queue.

**Rationale**: Round end + steal notification can happen in quick succession. Replacing would lose the first message. Queuing ensures all messages are seen. The queue will rarely exceed 2 items in practice.

**Alternatives considered**:
- Replace (latest wins) — simpler but loses messages. User specifically wants both round and steal dialogs visible.
- Stack (show all) — over-engineered. Multiple simultaneous overlays would be confusing.

## Decision 3: Rendering Approach

**Decision**: Use `ShapeElementList` for the background overlay/panel and `arcade.Text` for the message text. Both cached and rebuilt only on window resize.

**Rationale**: Constitution Principle I requires `ShapeElementList` and `arcade.Text` — no primitive draw calls allowed. Caching avoids GPU state rebuilds every frame.

**Alternatives considered**:
- UIManager widget — would work but is heavier than needed for a simple text overlay. UIManager dialogs are drawn last and would interfere with existing dialog z-ordering.
- `arcade.draw_rect_filled` — explicitly forbidden by constitution.

## Decision 4: Waiting Dialog Dismiss Strategy

**Decision**: Dismiss waiting dialogs in `_update_current_player()` as a catch-all, since this method is called whenever the turn advances or a waiting state resolves.

**Rationale**: Rather than adding dismiss calls to every individual handler (resource choice resolved, intrigue target resolved, etc.), a single dismiss in the turn-advance path covers all cases. Additional explicit dismiss calls can be added at specific resolution points for faster response.

**Alternatives considered**:
- Explicit dismiss in every resolution handler — correct but verbose and fragile (miss one handler = dialog stuck).
- Server-sent "dismiss" message — violates the "no server changes" constraint and adds protocol complexity.

## Decision 5: Sound Effect Scope

**Decision**: Play `sound2.mp3` only on round transitions. No sound for steal notifications or waiting dialogs.

**Rationale**: User specifically requested sound for round transitions. Steal notifications are brief and frequent — adding sound would be annoying. Waiting dialogs are passive states, not events.

**Alternatives considered**:
- Sound on all dialog types — potentially annoying, not requested.
- Configurable sound per dialog type — over-engineered for current needs (YAGNI).
