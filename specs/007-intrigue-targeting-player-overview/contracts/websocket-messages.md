# WebSocket Message Contracts: Intrigue Targeting & Player Overview

## New Client → Server Messages

### CancelIntrigueTargetRequest

Sent when the player cancels the intrigue target selection dialog.

```json
{
  "action": "cancel_intrigue_target"
}
```

**Preconditions**: Server has a pending_intrigue_target for this player.
**Server response**: Unwind backstage placement, broadcast PlacementCancelledResponse.

## Existing Client → Server Messages (No Changes)

### ChooseIntrigueTargetRequest

Already exists. Sent when the player selects a target opponent.

```json
{
  "action": "choose_intrigue_target",
  "target_player_id": "<player_id>"
}
```

**Preconditions**: Server has a pending_intrigue_target for this player. target_player_id is in eligible_targets.
**Server response**: Resolve effect, broadcast IntrigueEffectResolvedResponse.

## New Server → Client Messages

### IntrigueTargetPromptResponse

Sent to the active player when they must choose a target for their intrigue card.

```json
{
  "action": "intrigue_target_prompt",
  "effect_type": "steal_resources",
  "effect_value": {"guitarists": 0, "singers": 1, "coins": 0, ...},
  "eligible_targets": [
    {
      "player_id": "abc-123",
      "player_name": "Player 2",
      "resources": {
        "guitarists": 3,
        "bass_players": 1,
        "drummers": 0,
        "singers": 2,
        "coins": 5
      }
    }
  ]
}
```

**When sent**: After backstage placement when the intrigue card has effect_target "choose_opponent" and at least one eligible target exists.
**Recipient**: Only the active player (not broadcast).

### IntrigueEffectResolvedResponse

Broadcast to all clients after a targeted intrigue effect resolves.

```json
{
  "action": "intrigue_effect_resolved",
  "player_id": "abc-123",
  "target_player_id": "def-456",
  "effect_type": "steal_resources",
  "resources_affected": {
    "singers": 1
  }
}
```

**When sent**: After handle_choose_intrigue_target successfully resolves the effect.
**Recipient**: All players in the game (broadcast).

## Existing Server → Client Messages (Reused)

### PlacementCancelledResponse

Reused for cancel-during-targeting. The backstage slot space_id is "backstage_slot_N".

```json
{
  "action": "placement_cancelled",
  "player_id": "abc-123",
  "space_id": "backstage_slot_1",
  "next_player_id": null
}
```

## No-Valid-Targets Flow

When the server detects no eligible targets after backstage placement:
1. Server auto-unwinds the backstage placement
2. Sends ErrorResponse with code "NO_VALID_TARGETS" and message explaining why
3. Broadcasts PlacementCancelledResponse to unwind the slot on all clients
