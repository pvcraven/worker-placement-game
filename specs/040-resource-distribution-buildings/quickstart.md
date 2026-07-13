# Quickstart: Resource Distribution Buildings

## What This Feature Does

Adds 5 new purchasable buildings (7 coins each) that introduce the "place resources on action spaces" mechanic. When a player visits one of these buildings, they receive resources AND the building owner chooses other action spaces on the board where additional resources are placed from the supply. Those placed resources sit visibly on the target spaces until a future visitor collects them.

## Key Files to Modify

| File | What Changes |
|------|-------------|
| `shared/card_models.py` | Add `distribute_resource_type`, `distribute_per_space`, `distribute_space_count` fields to BuildingTile |
| `server/models/game.py` | Add `placed_resources` dict to ActionSpace, `pending_resource_distribution` to GameState |
| `shared/messages.py` | Add ResourceDistributionPromptResponse, ResourceDistributionRequest, ResourceDistributionResolvedResponse; extend WorkerPlacedResponse |
| `server/game_engine.py` | Handle distribution trigger in building visit flow, handle selection request, grant placed resources on space visit |
| `config/buildings.json` | Add 5 new building entries |
| `client/ui/board_renderer.py` | Render placed resource icons below worker token area |
| `client/views/game_view.py` | Handle new message types, update local state |
| `card-generator/generate_cards.py` | Generate card images for 5 new buildings with "Place:" text line |
| `server/models/config.py` | Update cost_coins validation range if needed (7 is within 3-8) |

## Implementation Order

1. **Data model** — Add fields to BuildingTile, ActionSpace, GameState
2. **Config** — Add 5 buildings to buildings.json
3. **Server: Collection** — Grant placed_resources to visitors on any space visit
4. **Server: Distribution flow** — Handle distribution trigger, pending state, selection
5. **Messages** — New message types for distribution prompt/request/resolved
6. **Client: State handling** — Process new messages, update local state
7. **Client: Rendering** — Display placed resource icons on spaces
8. **Card images** — Generate PNGs for 5 new buildings
9. **Tests** — Server logic tests for distribution, collection, edge cases

## How to Test

```bash
cd src && pytest && ruff check .
```

Manual test: Start server + client, purchase a distribution building, visit it, verify:
1. Visitor gets their resources
2. Owner is prompted to select target spaces
3. Resources appear on selected spaces
4. Next player visiting those spaces collects the placed resources
