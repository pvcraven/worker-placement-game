# Data Model: Quest Completion Animation

No new data models are introduced. This feature is client-side rendering only.

## Existing Entities Used

### QuestCompletedResponse (shared/messages.py)

Fields consumed by the animation:

| Field | Type | Usage in Animation |
|-------|------|--------------------|
| `player_id` | `str` | Look up player marker position for animation origin/destination |
| `contract_id` | `str` | Load quest card sprite from `quests/{contract_id}.png` |
| `resources_spent` | `dict` | Keys: guitarists, bass_players, drummers, singers, coins. Values drive the count and type of icons in the requirements stream |
| `bonus_resources` | `dict` | Same structure as resources_spent. Values drive the count and type of icons in the rewards stream |

### Resource Icon Mapping

| Resource Key | Icon File |
|-------------|-----------|
| `guitarists` | `client/assets/card_images/icons/guitarist.png` |
| `bass_players` | `client/assets/card_images/icons/bass_player.png` |
| `drummers` | `client/assets/card_images/icons/drummer.png` |
| `singers` | `client/assets/card_images/icons/singer.png` |
| `coins` | `client/assets/card_images/icons/coin.png` |

### Player Position

`GameView._player_marker_positions[pid]` → `tuple[float, float]` — the screen position of the player's marker in the upper-left area. Used as origin for requirement icons and destination for reward icons.

## State Changes

None. The animation is a visual overlay. All game state mutations (resource deduction, VP addition, card hand updates) continue to happen in the existing `_on_quest_completed` handler, independent of the animation.
