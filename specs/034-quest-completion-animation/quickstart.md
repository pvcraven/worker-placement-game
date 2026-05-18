# Quickstart: Quest Completion Animation

## What This Feature Does

Adds a visual animation sequence when a player completes a quest. The quest card flies to screen center, resource costs stream toward the card, resource rewards stream back to the player, and the card exits off-screen.

## Files to Modify

| File | Change |
|------|--------|
| `client/views/game_view.py` | Add `_enqueue_quest_completion_animation()`, `_start_quest_completion_animation()`, and resource streaming helper methods. Modify `_on_quest_completed()` to enqueue the animation. |

## Files Used (No Modification)

| File | Purpose |
|------|---------|
| `client/ui/animation_manager.py` | `AnimationManager.animate()` — drives all sprite movement and scaling |
| `client/ui/event_queue.py` | `EventQueue.enqueue()` with `AnimationEvent` — sequences with other animations |
| `client/assets/card_images/icons/*.png` | Resource icon sprites (guitarist, bass_player, drummer, singer, coin) |
| `client/assets/card_images/quests/*.png` | Quest card images |
| `shared/messages.py` | `QuestCompletedResponse` — provides resources_spent and bonus_resources data |

## Key Patterns to Follow

1. **Enqueue pattern** (from `_enqueue_intrigue_draw`):
   ```python
   anim_event = AnimationEvent(
       lambda gv, ...: gv._start_quest_completion_animation(..., anim_event),
   )
   self.event_queue.enqueue(anim_event, self)
   ```

2. **Callback chaining** (from `_start_card_pick_animation`):
   - Phase 1 `on_complete` → starts Phase 2
   - Phase 2 last icon `on_complete` → starts Phase 3
   - Phase 3 last icon `on_complete` → starts Phase 4
   - Phase 4 `on_complete` → `event.done = True`

3. **Player position lookup** (from existing animations):
   ```python
   origin = self._player_marker_positions.get(pid, (0.0, float(self.window.height)))
   ```

4. **Screen center** (from `_start_card_pick_animation`):
   ```python
   cx = self.window.width / 2
   cy = self.window.height / 2
   ```

## How to Test

1. Start server and client in separate terminals
2. Play until a quest can be completed (have enough resources)
3. Complete the quest
4. Observe the 4-phase animation sequence
5. Verify resource icon counts match the quest's cost and rewards
6. Verify gameplay resumes normally after the animation
