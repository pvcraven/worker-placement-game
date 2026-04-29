# Data Model: Shadow Studio + Bootleg Recording

**Date**: 2026-04-29

## New Config Entities

### Shadow Studio Building Tile (config/buildings.json)

| Field | Type | Value | Notes |
|-------|------|-------|-------|
| id | string | "building_023" | Next sequential building ID |
| name | string | "Shadow Studio" | Music-themed Zoarstar equivalent |
| description | string | "A mysterious studio that can mirror any other studio's session." | |
| cost_coins | int | 8 | Most expensive building in the game |
| visitor_reward | ResourceCost | all zeros | No base resource reward |
| visitor_reward_special | string | "copy_occupied_space" | New special value |
| visitor_reward_vp | int | 0 | No base VP |
| owner_bonus | ResourceCost | all zeros | No resource bonus for owner |
| owner_bonus_vp | int | 2 | 2 VP when visited by another player |

### Bootleg Recording Intrigue Cards (config/intrigue.json)

| Field | Type | Value | Notes |
|-------|------|-------|-------|
| id | string | "intrigue_053" / "intrigue_054" | Two copies |
| name | string | "Bootleg Recording" | |
| description | string | "Slip into a rival's studio and bootleg their session. Pay 2 coins to copy any opponent's occupied space." | |
| effect_type | string | "copy_occupied_space" | New effect type value |
| effect_target | string | "self" | Affects the card player |
| effect_value | dict | {"cost_coins": 2} | New key: cost_coins |

## Modified Server Models

### GameState (server/models/game.py)

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| pending_copy_source | dict \| None | None | Tracks active copy space selection |

**pending_copy_source structure** (when set):

```python
{
    "player_id": str,           # Player making the copy selection
    "source_space_id": str,     # Shadow Studio space or backstage slot ID
    "source_type": str,         # "building" or "intrigue"
    "cost_deducted": int,       # Coins deducted (intrigue only, 0 for building)
    "eligible_spaces": list,    # Filtered list of valid target spaces
}
```

## New Message Types (shared/messages.py)

### Client → Server

| Message | Action | Fields | Notes |
|---------|--------|--------|-------|
| SelectCopySpaceRequest | "select_copy_space" | space_id: str | Player selects target space |
| CancelCopySpaceRequest | "cancel_copy_space" | (none) | Player cancels selection |

### Server → Client

| Message | Action | Fields | Notes |
|---------|--------|--------|-------|
| CopySpacePromptResponse | "copy_space_prompt" | eligible_spaces: list[dict], source_type: str | Prompt for space selection |

**eligible_spaces entry structure**:

```python
{
    "space_id": str,
    "name": str,
    "space_type": str,
    "reward_preview": dict,  # ResourceCost dump for display
}
```

## State Transitions

### Shadow Studio Building Flow

```
Player places on Shadow Studio
  → [occupied check, reward grant, owner bonus for Shadow Studio]
  → pending_placement set, pending_copy_source set
  → CopySpacePromptResponse sent to player
  → Player selects space → handle_select_copy_space
    → _resolve_copied_space_rewards(target_space)
      → immediate: broadcast + quest check + advance turn
      → deferred: pending state for sub-flow (resource choice, quest selection, etc.)
  → Player cancels → handle_cancel_copy_space
    → _unwind_placement() for Shadow Studio
    → broadcast PlacementCancelledResponse
```

### Bootleg Recording Intrigue Card Flow

```
Player places on backstage slot, selects Bootleg Recording
  → _resolve_intrigue_effect checks coins + eligible spaces
    → insufficient_coins: unwind backstage, error message
    → no_valid_targets: unwind backstage, error message
    → ok: deduct 2 coins, set pending flags
  → pending_placement set (backstage), pending_copy_source set
  → CopySpacePromptResponse sent to player
  → Player selects space → handle_select_copy_space
    → _resolve_copied_space_rewards(target_space)
    → same resolution as building path
  → Player cancels → handle_cancel_copy_space
    → return 2 coins
    → _unwind_placement() for backstage slot
    → return intrigue card to hand
    → broadcast PlacementCancelledResponse
```
