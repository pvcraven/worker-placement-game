# Quickstart: Event Action Queue

## What This Feature Does

Adds a sequential event queue to the game client so that animations, dialogs, and sounds play one after another instead of overlapping. When a player picks a quest card, the card animation plays fully before the quest completion dialog appears.

## Key Files

| File | Role |
|------|------|
| `client/ui/event_queue.py` | **New** — EventQueue class and event types |
| `client/views/game_view.py` | Modified — message handlers enqueue events instead of showing directly |
| `client/ui/animation_manager.py` | Minor — animation completion callbacks signal the queue |

## How It Works

1. **Server sends a message** (e.g., `quest_card_selected`) → message handler in `game_view.py` receives it
2. **Handler creates an event** (e.g., AnimationEvent wrapping the card pick animation) and **enqueues** it
3. **Queue starts the event** immediately if nothing else is playing
4. **If another message arrives** (e.g., `quest_completion_prompt`) while an animation is active, the dialog event is enqueued — it waits
5. **When the animation finishes**, the queue starts the next event (the dialog), which now appears and is immediately interactive
6. **GameView.on_update()** calls `event_queue.update(dt)` each frame to advance the queue

## Adding a New Event Type

To queue a new kind of event:

1. Create a subclass of `QueuedEvent` with `start()`, `is_complete()`, and optionally `update(dt)`
2. In the message handler, create an instance and call `self.event_queue.enqueue(event)`

No changes to EventQueue itself are needed.

## Testing

- Server-side logic is unchanged — no new tests needed there
- The queue itself can be unit tested by creating mock events and verifying sequential processing
- Manual testing: play a game, trigger a quest pick from The Garage, verify the card animation plays before the completion dialog appears
