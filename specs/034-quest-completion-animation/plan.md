# Implementation Plan: Quest Completion Animation

**Branch**: `034-quest-completion-animation` | **Date**: 2026-05-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/034-quest-completion-animation/spec.md`

## Summary

Add a multi-phase animation sequence when a player completes a quest: the quest card flies from the upper-left to screen center at 2x scale, resource costs stream from the player position to the card, resource rewards stream back, and the card exits to the lower-right. Built entirely on the existing `AnimationManager` and `EventQueue` infrastructure with `on_complete` callback chaining.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (Easing, ease), Pydantic v2
**Storage**: N/A (client-side rendering only)
**Testing**: pytest + ruff (server logic); manual visual testing (client animations)
**Target Platform**: Desktop (Windows/macOS/Linux)
**Project Type**: Desktop game (client-server architecture)
**Performance Goals**: 60 fps maintained during animation; total sequence under 8 seconds
**Constraints**: Must use existing AnimationManager and EventQueue; no new dependencies
**Scale/Scope**: Single new animation sequence, ~2 files modified

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Uses Sprites and SpriteList via AnimationManager; no primitive draw calls |
| II. Pydantic Data Modeling | PASS | No new data models needed; uses existing QuestCompletedResponse message |
| III. Client-Server Separation | PASS | Animation is client-only rendering; no game state mutations; server already handles quest completion logic |
| IV. Test-Driven Game Logic | PASS | No server-side changes; animation is client UI only |
| V. Simplicity First | PASS | Reuses existing AnimationManager and EventQueue; no new abstractions |
| VI. Server-Authoritative Protocol | PASS | No new messages; hooks into existing QuestCompletedResponse handler |
| VII. Config-Driven Content | PASS | No new content types; reads quest cost/reward data from existing message |
| VIII. Pending State | N/A | No deferred actions |
| IX. Cancel/Unwind | N/A | Animation is non-interactive, not cancellable |
| X. Post-Action Turn Flow | PASS | Does not change turn flow; animation is visual feedback only |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/034-quest-completion-animation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
client/
  views/
    game_view.py           # MODIFY: add quest completion animation methods + enqueue in handler
  ui/
    animation_manager.py   # NO CHANGE: reuse as-is
    event_queue.py          # NO CHANGE: reuse as-is
  assets/
    card_images/
      icons/               # EXISTING: guitarist.png, bass_player.png, drummer.png, singer.png, coin.png
      quests/              # EXISTING: quest card images ({card_id}.png)
```

**Structure Decision**: All changes are in `client/views/game_view.py`. The existing animation infrastructure (`AnimationManager`, `EventQueue`, `AnimationEvent`) is reused without modification. Resource icon assets already exist in `client/assets/card_images/icons/`.

## Implementation Approach

### Phase-by-phase animation sequence

The quest completion animation is a single `AnimationEvent` enqueued on the `EventQueue`. Within that event, four phases are chained via `on_complete` callbacks:

**Phase 1 — Card Entrance**: Create a quest card sprite from its PNG. Animate from the player's marker position (upper-left) to screen center, scaling from 1x to 2x. Duration: ~0.5s. Easing: SINE.

**Phase 2 — Requirements Stream**: For each resource unit in `resources_spent`, create an icon sprite (from `client/assets/card_images/icons/`). Stagger starts by ~0.25s. Each icon animates from the player marker position to the card center and is removed on arrival. The AnimationManager already supports concurrent animations (multiple sprites in flight). The last icon's `on_complete` triggers Phase 3.

**Phase 3 — Rewards Stream** (conditional): If `bonus_resources` has any non-zero values, create icon sprites at the card center and animate them to the player marker position, staggered similarly. Skip if no resource rewards. The last icon's `on_complete` triggers Phase 4.

**Phase 4 — Card Exit**: Animate the quest card from center to lower-right corner (off-screen), scaling back down. Duration: ~0.75s. Easing: QUAD_IN. On complete, set `event.done = True` to unblock the EventQueue.

### Integration point

In `_on_quest_completed()`, before the existing state update logic, enqueue the animation event. The state updates (resource deduction, VP addition, log entries) happen immediately as they do now — the animation is purely visual overlay. The `next_player_id` update and any drawn intrigue card animations are enqueued after the quest completion animation, so they sequence naturally.

### Resource icon mapping

Reuse the existing `_RESOURCE_CONFIG` mapping from `resource_bar.py`:
- `guitarists` → `client/assets/card_images/icons/guitarist.png`
- `bass_players` → `client/assets/card_images/icons/bass_player.png`
- `drummers` → `client/assets/card_images/icons/drummer.png`
- `singers` → `client/assets/card_images/icons/singer.png`
- `coins` → `client/assets/card_images/icons/coin.png`

### Player position

Use `self._player_marker_positions[pid]` as the origin/destination for resource icons, consistent with existing card pick and intrigue animations. Fallback: `(0.0, float(self.window.height))` for upper-left if position not found.
