# Research: Resource Choice Rewards

**Feature**: 012-resource-choice-rewards
**Date**: 2026-04-19

## No NEEDS CLARIFICATION items

All technical decisions are informed by existing codebase patterns. No external research required.

## Decisions

### 1. Choice reward data representation

**Decision**: Add `ResourceChoiceReward` Pydantic model to `shared/card_models.py` with a `choice_type` discriminator field.

**Rationale**: The existing codebase already uses Pydantic models for all structured data. A single model with `choice_type` in `("pick", "bundle", "combo", "exchange")` covers all 7 scenarios without needing multiple model classes.

**Alternatives considered**:
- Separate model classes per choice type (e.g., `PickReward`, `BundleReward`) — rejected because the differences are small (a few optional fields) and a union would add complexity for the config loader
- String-encoded DSL in `visitor_reward_special` — rejected because it would bypass Pydantic validation and be harder to extend

### 2. Server pending state management

**Decision**: Add `pending_resource_choice: dict | None` to `GameState`, following the exact pattern of `pending_intrigue_target` and `pending_quest_reward`.

**Rationale**: Proven pattern in the codebase. The game engine checks for pending state before advancing turns, sends prompts, and clears state when resolved.

**Alternatives considered**:
- Separate state machine class for choice resolution — rejected per Simplicity First principle; the existing dict-based pending state is sufficient

### 3. Client dialog approach

**Decision**: Single `ResourceChoiceDialog` class in `client/ui/dialogs.py` using `arcade.gui` widgets with mode-based rendering.

**Rationale**: Existing dialogs (`CardSelectionDialog`, `RewardChoiceDialog`, `PlayerTargetDialog`, `BuildingPurchaseDialog`) all use `arcade.gui.UIBoxLayout` with buttons. The pick and bundle modes are straightforward button lists. The combo mode needs +/- buttons and a total label, which is still simple with `arcade.gui`.

**Alternatives considered**:
- Three separate dialog classes — rejected because they share 80% of the layout code (title, description, background, show/hide)
- Custom rendering without arcade.gui — rejected per Constitution Principle I

### 4. Multi-player choice sequencing

**Decision**: Server sends prompts one player at a time in turn order. Each prompt is a standard `resource_choice_prompt` message. The server tracks remaining players in `pending_resource_choice["remaining_players"]`.

**Rationale**: Sequential prompting is simpler than parallel (no race conditions, no need for barrier synchronization). The existing intrigue target selection is already sequential. Players see their prompt only when it's their turn to choose.

**Alternatives considered**:
- Parallel prompting to all players at once — rejected because it complicates state management and the client would need to handle a prompt arriving while another player's prompt is active

### 5. Config extension approach

**Decision**: Add 4 new buildings and 2 new intrigue cards to existing JSON config files. New buildings use `visitor_reward_choice` field; new intrigue cards use `choice_reward` field with `effect_type: "resource_choice"`.

**Rationale**: Extends existing config format non-destructively. Old buildings/intrigue cards continue to work unchanged. The server checks for the new optional field and falls through to existing reward logic if absent.

**Alternatives considered**:
- Separate config file for choice rewards — rejected because it would scatter building definitions across files
- Modifying existing buildings to have choices — rejected because it would change game balance
