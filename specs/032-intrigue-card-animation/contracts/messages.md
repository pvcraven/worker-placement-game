# Message Contract Changes: Intrigue Card Animation

**Date**: 2026-05-16

## Modified Messages

### IntrigueEffectResolvedResponse

**Direction**: Server → All Clients (broadcast)
**Action**: `"intrigue_effect_resolved"`

| Field | Type | Change | Description |
|-------|------|--------|-------------|
| player_id | str | existing | Player who played the card |
| target_player_id | str | existing | Player affected by the card |
| effect_type | str | existing | Type of effect applied |
| resources_affected | dict | existing | Resource changes |
| intrigue_card_id | str | **new** | ID of the played intrigue card |
| intrigue_card_name | str | **new** | Display name of the played card |

**Backward compatibility**: New fields default to `""`, so older clients ignore them.

## Unchanged Messages (used for draw animation)

### QuestCompletedResponse

Already includes `drawn_intrigue: list[dict]` with full card data (id, name, description, effects). Used by the draw animation to determine face-up card sprite for the local player.

### WorkerPlacedBackstageResponse

Already includes `intrigue_card: dict` with card id, name, and description. Used by the draw animation for backstage intrigue draws.

## No New Messages

All animation logic uses existing message types. No new request/response pairs are needed.
