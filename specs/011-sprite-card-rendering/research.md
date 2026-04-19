# Research: Sprite Card Rendering

**Feature**: Sprite Card Rendering
**Date**: 2026-04-18

## Decision 1: SpriteList Organization Strategy

**Decision**: One SpriteList per rendering context (board quests, board buildings, hand panel, dialog)
**Rationale**: Each rendering context has an independent lifecycle — board sprites persist across frames, hand panel sprites are created/destroyed on toggle, dialog sprites are ephemeral. Per-context lists allow independent updates without rebuilding unrelated sprite lists. The user's original request allowed "all in one sprite list, or a sprite list for each type" — per-context is a natural extension that avoids cross-context coupling.
**Alternatives considered**:
- Single SpriteList for all cards — simpler but requires rebuilding the entire list when any context changes, and complicates position management
- Per-type SpriteList (all quests in one, all buildings in one) — problematic because the same card type appears in multiple contexts (quest cards on board AND in hand panel AND in dialog) with different positions

## Decision 2: Sprite Loading Strategy

**Decision**: Load sprites from PNG file path using `arcade.Sprite(path, center_x=x, center_y=y)`. Arcade's texture cache handles deduplication automatically.
**Rationale**: Arcade internally caches textures by file path. Loading the same card image in multiple contexts (e.g., a quest card on the board and in the hand panel) reuses the GPU texture. No custom caching needed.
**Alternatives considered**:
- Pre-load all textures at startup — unnecessary, arcade already caches on first load
- Use arcade.load_texture() explicitly — adds indirection without benefit

## Decision 3: Highlight Rendering

**Decision**: Draw `arcade.draw_rect_outline()` over highlighted sprites using the sprite's position and dimensions
**Rationale**: Only 1-2 cards are highlighted at a time, so the performance cost of individual draw calls is negligible. Arcade sprites don't have a built-in outline feature. Using a separate "highlight sprite" overlay would add complexity for minimal gain.
**Alternatives considered**:
- Tinting the sprite via `sprite.color` — changes the card appearance rather than adding an outline
- Drawing a slightly larger sprite behind — requires maintaining a parallel set of highlight sprites
- Using `SpriteList.draw_hit_boxes()` — debug visualization only, not suitable for production

## Decision 4: SpriteList Rebuild Triggers

**Decision**: Rebuild each SpriteList when the underlying card data changes, triggered by existing message handlers
**Rationale**: The game already has clear update points — `update_board()` for board state, `_handle_message()` for hand changes, dialog `show()` for dialog cards. Rebuilding the SpriteList at these points (clear + re-add) is simple and correct. Card counts are small (max ~6 per context), so rebuild cost is negligible.
**Alternatives considered**:
- Diff-based updates (only add/remove changed sprites) — over-engineered for lists of 3-6 sprites
- Dirty flag with lazy rebuild on draw — adds complexity for no measurable benefit with small sprite counts

## Decision 5: CardRenderer Cleanup

**Decision**: Remove `card_renderer.py` entirely after all 5 call sites are converted
**Rationale**: Once all rendering uses sprites, the CardRenderer class (with its rect draws, text caching, and genre color mapping) is dead code. The `get_card_rect()` static method can be replaced by sprite bounding boxes. The `_CARD_WIDTH` and `_CARD_HEIGHT` constants can move to a shared location or be derived from sprite dimensions.
**Alternatives considered**:
- Keep CardRenderer as fallback — adds maintenance burden for unused code
- Keep only constants — can be defined where needed or derived from sprite size

## Decision 6: Missing Card Image Handling

**Decision**: Log a warning and skip rendering for cards whose PNG file doesn't exist
**Rationale**: Missing images indicate a card generator issue, not a runtime problem. Crashing would be worse than a missing card. The `ensure_card_images()` startup check should prevent this scenario in normal operation.
**Alternatives considered**:
- Render a placeholder rectangle — adds complexity for an edge case that shouldn't occur
- Fall back to CardRenderer — keeps dead code alive for error handling
