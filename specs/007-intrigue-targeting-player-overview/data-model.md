# Data Model: Intrigue Targeting & Player Overview

## Modified Entities

### GameState (server/models/game.py)

New field to track pending intrigue target selection:

```
pending_intrigue_target: Optional dict
  - player_id: str (who played the card)
  - slot_number: int (which backstage slot)
  - intrigue_card: IntrigueCard (the played card)
  - effect_type: str ("steal_resources" or "opponent_loses")
  - effect_value: dict (resource amounts)
  - eligible_targets: list[str] (player_ids who can be targeted)
```

**Lifecycle**: Set when a "choose_opponent" intrigue card is played on a backstage slot. Cleared when target is selected or cancel is triggered. Only one pending target can exist at a time (turn-based game).

## New Messages

### IntrigueTargetPromptResponse (server → client)

Sent to the active player when they need to choose a target.

```
action: "intrigue_target_prompt"
effect_type: str
effect_value: dict
eligible_targets: list[{player_id, player_name, resources}]
```

### IntrigueEffectResolvedResponse (server → all clients)

Broadcast after a targeted intrigue effect resolves.

```
action: "intrigue_effect_resolved"
player_id: str (who played the card)
target_player_id: str (who was targeted)
effect_type: str
resources_affected: dict
```

### CancelIntrigueTargetRequest (client → server)

Sent when the player cancels target selection.

```
action: "cancel_intrigue_target"
```

## Unchanged Entities

- **IntrigueCard** (shared/card_models.py): No changes — effect_type, effect_target, effect_value already sufficient.
- **Player** (server/models/game.py): No changes — resources, intrigue_hand, available_workers already exist.
- **BackstageSlot** (server/models/game.py): No changes — occupied_by, intrigue_card_played already exist.
- **ChooseIntrigueTargetRequest** (shared/messages.py): Already exists with target_player_id field.

## Player Overview Panel Data

No new data model needed. The panel reads existing fields from the game state:

From each player dict:
- `display_name`
- `available_workers` / `total_workers`
- `resources.guitarists`, `resources.bass_players`, `resources.drummers`, `resources.singers`, `resources.coins`
- `intrigue_hand_count` (for opponents) or `len(intrigue_hand)` (for self)
- `contract_hand_count` (for opponents) or `len(contract_hand)` (for self)
- `completed_quests` (count)
- `victory_points`
