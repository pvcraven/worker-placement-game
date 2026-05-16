# Event Queue Interface Contract

## EventQueue Public API

### enqueue(event: QueuedEvent) → None
Add an event to the queue. If the queue is idle (no current event), the event starts immediately.

### update(dt: float) → None
Called each frame from GameView.on_update(). Checks if the current event is complete and advances to the next event if so.

### is_busy() → bool
Returns True if there is an active event or pending events in the queue. Used by game logic that needs to wait for the queue to drain (e.g., round-end transitions).

## QueuedEvent Interface

### start(game_view) → None
Begin the event. Called by EventQueue when this event becomes the active event.

### is_complete() → bool
Returns True when the event has finished and the queue should advance.

### update(dt: float) → None
Optional per-frame update. Called by EventQueue each frame while this event is active. Default is no-op.

## Integration Points

### GameView owns the EventQueue
- Created in `GameView.__init__`
- `update(dt)` called in `GameView.on_update`
- Message handlers call `self.event_queue.enqueue(...)` instead of directly showing dialogs/animations

### Existing dialog callbacks must signal completion
- Dialog `on_select`/`on_skip`/`on_cancel` callbacks set `event.done = True` in addition to their existing cleanup
- This replaces the pattern of setting dialog reference to None as the sole completion signal
