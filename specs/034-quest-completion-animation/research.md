# Research: Quest Completion Animation

## R1: Animation chaining with staggered concurrent sprites

**Decision**: Use `AnimationManager.animate()` with staggered `on_complete` callbacks to create the streaming effect. Start each resource icon animation 0.25s after the previous one using a delayed-start pattern: the first icon animates immediately, and its setup schedules the next icon after a brief delay by using a short "hold" animation (0.25s duration at the origin point) whose `on_complete` starts the next icon's flight.

**Rationale**: The AnimationManager already supports multiple concurrent animations. The `on_complete` callback on each animation provides the sequencing hook. Using a short hold animation as a delay timer avoids introducing any new timer mechanism and stays within the existing animation system.

**Alternatives considered**:
- **Python `asyncio.sleep`**: Would require threading coordination with Arcade's event loop — unnecessary complexity.
- **Custom timer in `update()`**: Would require new state tracking outside the animation system — violates Simplicity First.
- **All-at-once animation**: Loses the streaming visual effect specified in the feature.

## R2: Resource icon sprite creation

**Decision**: Load resource icon sprites from `client/assets/card_images/icons/{resource_name}.png` using `arcade.Sprite`. These assets already exist and are used by the resource bar.

**Rationale**: Icons are small PNGs already present in the asset pipeline. No new asset generation needed. The resource-to-filename mapping matches `_RESOURCE_CONFIG` in `resource_bar.py`.

**Alternatives considered**:
- **Generate icons at runtime**: Unnecessary — assets already exist.
- **Use text labels instead of icons**: Less visually appealing and inconsistent with the game's sprite-based aesthetic.

## R3: Tracking when all staggered animations complete

**Decision**: Track the total number of resource icons to animate. Maintain a counter that decrements in each icon's `on_complete`. When the counter reaches zero, trigger the next phase.

**Rationale**: Simple counter pattern avoids complex state machines. Each icon's `on_complete` callback handles its own cleanup (sprite removal is automatic via AnimationManager) and decrements the shared counter. Thread safety is not a concern since all callbacks execute in the main Arcade event loop.

**Alternatives considered**:
- **Wait for AnimationManager to be empty**: Would break if other unrelated animations are also active.
- **Track individual animation objects**: Overengineered for a simple count-down scenario.

## R4: Edge case — quest with zero resource cost

**Decision**: If `resources_spent` has all zero values, skip Phase 2 entirely and proceed directly to Phase 3 (rewards) or Phase 4 (exit).

**Rationale**: The streaming effect requires at least one icon. Showing nothing for 0 seconds is correct — just skip to the next phase.

## R5: Edge case — quest with no resource rewards

**Decision**: If `bonus_resources` has all zero values (or is empty), skip Phase 3 and proceed directly to Phase 4 (card exit).

**Rationale**: Consistent with the conditional logic described in the spec. Non-resource rewards (VP, intrigue draws, buildings) are already handled by existing UI updates and log entries.

## R6: Card sprite for the animation

**Decision**: Create the quest card sprite from `client/assets/card_images/quests/{contract_id}.png`, using the same pattern as `_start_card_pick_animation`. The card image is already generated and available.

**Rationale**: Exact same approach used by the existing card pick animation (line 988 of game_view.py). Consistent and proven.
