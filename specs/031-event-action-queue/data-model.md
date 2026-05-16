# Data Model: Event Action Queue

## Entities

### QueuedEvent (abstract base)

Represents a single presentational event to show the player.

| Field | Type | Description |
|-------|------|-------------|
| started | bool | Whether the event has been started |

**Behaviors**:
- `start(game_view)` — Begin the event (play animation, show dialog, play sound)
- `is_complete()` → bool — Whether the event has finished
- `update(dt)` — Per-frame update (optional, used by timed events)

### AnimationEvent (extends QueuedEvent)

An event that plays one or more animations via the existing AnimationManager.

| Field | Type | Description |
|-------|------|-------------|
| setup_fn | callable | Function that sets up the animation(s) and starts them |
| done | bool | Set to True by the animation's on_complete callback |

**Completion**: The animation's final `on_complete` callback sets `done = True`.

### DialogEvent (extends QueuedEvent)

An event that shows a dialog and waits for player interaction.

| Field | Type | Description |
|-------|------|-------------|
| show_fn | callable | Function that creates and shows the dialog |
| done | bool | Set to True when dialog callback fires |
| sound | Sound or None | Optional sound to play when the dialog appears |

**Completion**: The dialog's `on_select`/`on_skip`/`on_cancel` callback sets `done = True`.

### SoundEvent (extends QueuedEvent)

A standalone sound effect with no visual component.

| Field | Type | Description |
|-------|------|-------------|
| sound | Sound | The sound to play |
| duration | float | How long to wait before completing (seconds) |
| elapsed | float | Time elapsed since start |

**Completion**: When `elapsed >= duration`.

### EventQueue

The manager that processes events sequentially.

| Field | Type | Description |
|-------|------|-------------|
| queue | list[QueuedEvent] | Pending events in FIFO order |
| current | QueuedEvent or None | The event currently playing |

**Behaviors**:
- `enqueue(event)` — Add an event. If nothing is active, start it immediately.
- `update(dt)` — Called each frame. Checks if current event is complete; if so, starts next.
- `is_busy()` → bool — Whether there is an active or pending event.

## Relationships

```
EventQueue 1 ──── * QueuedEvent
                     ├── AnimationEvent
                     ├── DialogEvent
                     └── SoundEvent
```

## State Transitions

```
EventQueue states:
  IDLE → event enqueued → PROCESSING → event completes → more events? → PROCESSING
                                                        → no events?  → IDLE

QueuedEvent states:
  PENDING → start() called → ACTIVE → is_complete() returns True → DONE
```
