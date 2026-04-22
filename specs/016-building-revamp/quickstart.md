# Quickstart: Building Revamp

## How to Test

### 1. Run existing tests (should pass without changes)
```bash
cd "c:/Users/PaCra/Worker Placement Game" && python -m pytest tests/ -v
```

### 2. Run new building tests
```bash
python -m pytest tests/test_buildings.py -v
```

### 3. Manual gameplay test

Start server and client:
```bash
# Terminal 1
cd "c:/Users/PaCra/Worker Placement Game" && python -m server.main

# Terminal 2
cd "c:/Users/PaCra/Worker Placement Game" && python -m client.main
```

**Test scenarios**:

1. **Accumulating building**: Purchase a guitarist accumulation building. Pass turns until next round. Verify stock increases. Visit the building and confirm you receive all accumulated guitarists.

2. **VP building**: Purchase the VP accumulation building. Let it accumulate across rounds. Visit it and verify VP total increases and quest pick is offered.

3. **Owner choice**: Have Player A purchase a multi-resource building (Category D). Have Player B visit it. Verify Player A gets a choice prompt for their owner bonus.

4. **Spend-to-get**: Visit a Category C building. Verify coins are deducted before resource choice is presented. Try visiting when you can't afford it — should be blocked.

5. **Exchange**: Visit the exchange building. Return 2 resources, pick 3. Verify transaction.

6. **draw_contract / draw_intrigue**: Visit buildings with these specials. Verify quest pick or intrigue draw occurs.

### 4. Generate building card images
```bash
cd "c:/Users/PaCra/Worker Placement Game" && python card-generator/generate_cards.py
```

## Key Files to Modify

| File | Change |
|------|--------|
| `config/buildings.json` | Replace 28 buildings with 20 new ones |
| `shared/card_models.py` | Add accumulation, VP, owner choice fields to BuildingTile |
| `server/game_engine.py` | Accumulation at round start, VP grants, owner choice flow, visitor_reward_special |
| `server/config_loader.py` | Validate new building fields |
| `server/lobby.py` | Set accumulation_initial on purchase |
| `client/ui/board_renderer.py` | Display accumulated stock on buildings |
| `card-generator/generate_cards.py` | Generate PNGs for 20 new buildings |
| `tests/test_buildings.py` | New test file for building mechanics |
