# Data Model: Sprite Card Rendering

**Feature**: Sprite Card Rendering
**Date**: 2026-04-18

## Existing Models (unchanged)

No data models are created or modified by this feature. Card data continues to flow as dicts from the server via game state. The card PNG images are pre-generated assets loaded as arcade textures.

## New Runtime State (per rendering context)

No persistent data. The following transient state is added to existing classes:

### BoardRenderer (board_renderer.py)

| Field | Type | Purpose |
|-------|------|---------|
| _quest_sprite_list | arcade.SpriteList | Batch-rendered face-up quest card sprites |
| _building_sprite_list | arcade.SpriteList | Batch-rendered face-up building card sprites |

### GameView (game_view.py)

| Field | Type | Purpose |
|-------|------|---------|
| _hand_sprite_list | arcade.SpriteList | Batch-rendered hand panel card sprites (quest or intrigue) |

### QuestCompletionDialog (dialogs.py)

| Field | Type | Purpose |
|-------|------|---------|
| _quest_sprite_list | arcade.SpriteList | Batch-rendered quest card sprites in the dialog |

## Card Image Path Convention

Card ID maps directly to PNG filename:

| Card Type | Path Pattern | Example |
|-----------|-------------|---------|
| Quest | `client/assets/card_images/quests/{card_id}.png` | `quests/contract_jazz_001.png` |
| Building | `client/assets/card_images/buildings/{card_id}.png` | `buildings/building_001.png` |
| Intrigue | `client/assets/card_images/intrigue/{card_id}.png` | `intrigue/intrigue_019.png` |

## Constants

| Constant | Value | Source |
|----------|-------|--------|
| Card width | 190px | Derived from sprite dimensions (matches existing _CARD_WIDTH) |
| Card height | 230px | Derived from sprite dimensions (matches existing _CARD_HEIGHT) |
