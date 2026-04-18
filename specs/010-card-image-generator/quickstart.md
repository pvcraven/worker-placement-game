# Quickstart: Card Image Generator

**Feature**: Card Image Generator
**Date**: 2026-04-18

## Prerequisites

- Python 3.12+
- Pillow installed (`uv pip install Pillow` or added to pyproject.toml)
- Project root as working directory

## Run the Generator

```bash
python card-generator/generate_cards.py
```

## Expected Output

```
Generating quest cards... 66 cards written to client/assets/card_images/quests/
Generating building cards... 24 cards written to client/assets/card_images/buildings/
Generating intrigue cards... 50 cards written to client/assets/card_images/intrigue/
Generating producer cards... 11 cards written to client/assets/card_images/producers/
Done. 151 card images generated.
```

## Verification Scenarios

### Scenario 1: All Cards Generated

1. Run `python card-generator/generate_cards.py`
2. Count files: `ls client/assets/card_images/quests/ | wc -l` → 66
3. Count files: `ls client/assets/card_images/buildings/ | wc -l` → 24
4. Count files: `ls client/assets/card_images/intrigue/ | wc -l` → 50
5. Count files: `ls client/assets/card_images/producers/ | wc -l` → 11

### Scenario 2: Quest Card Visual Check

1. Open `client/assets/card_images/quests/contract_jazz_001.png`
2. Verify: transparent background, parchment-colored rounded rectangle
3. Verify: blue genre band at top with "JAZZ" text
4. Verify: card name "Midnight Jazz Ensemble" below genre band
5. Verify: cost line shows "1G 1B 1D"
6. Verify: "4 VP" displayed prominently
7. Verify: bonus line shows "+2$"
8. Verify: description text is readable dark brown on parchment

### Scenario 3: Building Card Visual Check

1. Open `client/assets/card_images/buildings/building_001.png`
2. Verify: parchment background with rounded corners
3. Verify: "Abbey Road Studios" as card name
4. Verify: "Cost: 6 coins"
5. Verify: visitor reward shows "1G 1B 1D"
6. Verify: owner bonus shows "2$"
7. Verify: description text is readable

### Scenario 4: Intrigue Card Visual Check

1. Open `client/assets/card_images/intrigue/intrigue_019.png`
2. Verify: "Contract Buyout" as card name
3. Verify: description text visible
4. Verify: effect summary shows "Steal 1G"
5. Verify: target indicator shows targeting info

### Scenario 5: Producer Card Visual Check

1. Open `client/assets/card_images/producers/producer_001.png`
2. Verify: "Quincy Jones" as card name
3. Verify: bonus genres "Jazz, Pop" displayed
4. Verify: "+4 VP per contract" displayed
5. Verify: description text visible

### Scenario 6: Long Name Truncation

1. Find a card with a name longer than 20 characters
2. Verify the name is truncated with ".." suffix

### Scenario 7: Idempotent Regeneration

1. Run the script twice
2. Verify output files are overwritten without errors
3. Verify file count remains the same (151 total)

### Scenario 8: Plot Quest Marker

1. Find a quest card with `is_plot_quest: true` in contracts.json
2. Verify the card image shows a visual indicator for plot quest status

### Scenario 9: Building Special Rewards

1. Open `client/assets/card_images/buildings/building_004.png` (FAME Studios)
2. Verify: visitor_reward_special "draw_contract" is displayed (e.g., "Draw Quest" or similar)

### Scenario 10: Intrigue All-Players Effect

1. Open `client/assets/card_images/intrigue/intrigue_047.png` (Charity Concert)
2. Verify: effect shows resources gained and "(all players)" indicator

### Scenario 11: Performance

1. Time the script: `time python card-generator/generate_cards.py`
2. Verify: completes in under 30 seconds
