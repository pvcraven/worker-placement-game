# Research: Resource Bar Revamp

## Decision 1: Resource Icon PNG Size and Style

**Decision**: Generate resource icon PNGs at 72x72 pixels (2x the _SYMBOL_SIZE of 36), matching the 2x resolution approach used for quest and space cards. Each icon is a single resource symbol (colored square or gold circle) with black outline on transparent background.

**Rationale**: The 2x approach is already established in the project for quest and space cards (generated at 2x, rendered at 0.5x scale). Using transparent backgrounds allows the icons to composite cleanly over the parchment background without needing exact color matching at generation time.

**Alternatives considered**:
- 36x36 (1x): Would look pixelated when scaled up on larger windows
- 144x144 (4x): Unnecessarily large file sizes for small inline icons
- Opaque parchment background in PNG: Would create visible seams if parchment color ever changes

## Decision 2: Card Icon PNG Generation

**Decision**: Generate standalone quest_icon.png and intrigue_icon.png by reusing the existing `_draw_card_icon()` function. Output at 2x the current _CARD_ICON_W/_CARD_ICON_H (84x114 pixels) with transparent background.

**Rationale**: The card icon drawing code already exists and produces the correct visual. Extracting to standalone PNGs follows the same pattern as resource icons and enables SpriteList usage in the resource bar.

**Alternatives considered**:
- Draw card icons as shapes in the resource bar: Would violate Constitution Principle I (no primitive draw calls)
- Crop icons from space card PNGs: Fragile, depends on exact positioning

## Decision 3: Parchment and Text Colors

**Decision**: Use the exact values from the card generator:
- Background: `PARCHMENT_COLOR = (235, 220, 185)`
- Text: `TEXT_COLOR = (60, 40, 20)`
- Font: Tahoma (already used in resource bar, matches `FONT_NAME` in card generator)

**Rationale**: Direct reuse of established constants ensures visual consistency. Tahoma is already the font in both the card generator and the resource bar.

**Alternatives considered**:
- Slightly different shade for differentiation: User explicitly requested "same parchment color as the cards"

## Decision 4: SpriteList Caching Strategy

**Decision**: The resource bar maintains a single SpriteList containing all icon sprites. It is rebuilt only when `update_resources()` is called with changed data or when the panel geometry changes (resize). A dirty flag tracks whether a rebuild is needed.

**Rationale**: This follows the same caching pattern used in `board_renderer.py` and `tabbed_panel.py` throughout the project. Comparing a tuple key of current values avoids unnecessary rebuilds.

**Alternatives considered**:
- Separate SpriteLists per icon type: Over-engineered for ~12 sprites
- Always rebuild: Violates FR-005 (no per-frame recreation)

## Decision 5: Player Color Mapping for Worker Marker

**Decision**: The resource bar receives the player's color name (e.g., "red") and loads `client/assets/card_images/markers/worker_{color}.png`. The game_view already knows the player's color from the game state.

**Rationale**: Worker marker PNGs already exist for all 5 colors. The game_view already maps player IDs to colors via `_player_colors`.

**Alternatives considered**:
- Generate new smaller marker icons: Unnecessary — existing markers can be scaled down via sprite.scale

## Decision 6: Icon Output Directory

**Decision**: Store generated icon PNGs in `client/assets/card_images/icons/`. This is a new subdirectory alongside the existing `quests/`, `buildings/`, `spaces/`, `markers/` directories.

**Rationale**: Keeps icon PNGs organized separately from full-size card images. The `markers/` directory is reserved for player-colored worker tokens.

**Alternatives considered**:
- Put in `markers/`: Would mix resource symbols with player markers
- Put in root `card_images/`: Would clutter the directory with many small files
