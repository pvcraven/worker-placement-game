# Data Model: Informational Dialog System

## Entities

### InfoDialog (Client-Side UI Component)

A transient overlay that displays centered text messages on the game view.

| Field | Type | Description |
|-------|------|-------------|
| _queue | list[tuple[str, float \| None]] | FIFO queue of pending messages. Each entry is (message_text, duration_seconds_or_None). |
| _active_message | str \| None | Currently displayed message text. None when no dialog is visible. |
| _active_duration | float \| None | Auto-dismiss duration in seconds. None for persistent dialogs. |
| _elapsed | float | Accumulated time since current message was shown. Reset on each new message. |
| _bg_shapes | ShapeElementList | Cached GPU shapes for the background overlay and panel. |
| _text_obj | arcade.Text | Cached text object for the message. Reused across messages. |
| _dirty | bool | Flag indicating shapes need rebuild (e.g., after window resize). |

### State Transitions

```
IDLE → SHOWING (show() called with message)
SHOWING → IDLE (dismiss() called, queue empty)
SHOWING → SHOWING (dismiss() called, queue has next item → show next)
SHOWING → IDLE (auto-dismiss timer expires, queue empty)
SHOWING → SHOWING (auto-dismiss timer expires, queue has next item)
```

### Lifecycle

1. Created once in `GameView.__init__`
2. `show()` enqueues messages; displays immediately if idle
3. `update(dt)` called every frame from `on_update`; manages auto-dismiss countdown
4. `draw(w, h, scale)` called every frame from `on_draw`; renders if active
5. `dismiss()` called by game events (waiting state resolved) or auto-dismiss timer
6. Lives for the lifetime of the GameView

## Relationships

- **GameView** → owns one **InfoDialog** instance
- **InfoDialog** has no dependencies on game state, server messages, or other UI components
- Message handlers in **GameView** call `InfoDialog.show()` and `InfoDialog.dismiss()`

## No Server-Side Entities

This feature adds no server models, no network messages, and no config entries.
