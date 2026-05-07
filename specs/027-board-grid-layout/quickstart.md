# Quickstart: Board Grid Layout

**Feature**: 027-board-grid-layout
**Date**: 2026-05-06

## Manual Test Scenarios

### Scenario 1: Grid Alignment Verification

1. Start a 2-player game
2. Observe the board layout:
   - 8 permanent action spaces in a vertical column on the left (column 0)
   - Sunset Records, The Back Room, The Garage across the top (columns 3.5, 4.5, 5.5)
   - 3 backstage slots in column 3 (rows 0-2)
   - Realtor space in column 3, row 4
   - 4 face-up quest cards in the center-right area
   - 3 face-up building market cards in the lower-right area
3. Verify: All elements are aligned to grid cells with uniform spacing, no overlaps

### Scenario 2: Window Resize

1. Start a game and observe the layout
2. Resize the window by dragging edges (make it wider, narrower, taller, shorter)
3. Verify: All elements reposition smoothly without overlap or jitter
4. Verify: Side panel width scales proportionally with the board
5. Verify: Card sizes remain proportional (no card type grows/shrinks independently)

### Scenario 3: Click Detection

1. Start a 2-player game
2. Click on each permanent action space — verify it highlights/responds correctly
3. Click on each backstage slot — verify correct response
4. Click on the realtor space — verify correct response
5. Click on each face-up quest card — verify info dialog or action triggers
6. Click on each face-up building market card — verify correct response
7. Place workers on various spaces — verify they snap to correct positions

### Scenario 4: Building Purchase Layout

1. Start a game and purchase buildings
2. First building should appear in column 1, row 0
3. Second building in column 2, row 0
4. Third building in column 1, row 1.5
5. Continue purchasing — buildings fill columns 1-2, stacking at 1.5-row intervals
6. Verify: Worker tokens appear correctly on constructed buildings
7. Verify: Owner names display correctly below buildings

### Scenario 5: Multi-Player Consistency

1. Start games with 2, 3, 4, and 5 players
2. Verify: Grid layout is identical in all player counts
3. Verify: Only the number of occupied spaces changes, not the layout

### Scenario 6: Extreme Window Sizes

1. Resize window to minimum (~800px wide)
2. Verify: Elements are still readable and don't clip
3. Resize to very large (~2560px wide)
4. Verify: Elements scale up proportionally, no visual artifacts

## Expected Layout (Visual Reference)

```
Row 0: [Merch]  [Bld1]  [Bld2]  [BS1] [SunR]  [----]  [BackR]  [----]  [Garg]
Row 1: [Motwn]  [----]  [----]  [BS2]
Row 2: [GuitC]  [Bld3]  [Bld4]  [BS3]         [Quest1] [Quest2]
Row 3: [TalSh]  [----]  [----]  [---]         [------] [------]
Row 4: [RhytP]  [Bld5]  [Bld6]  [Rltr]       [------] [------]
Row 5: [JamSs]  [----]  [----]                [Quest3] [Quest4]  [BldM1]
Row 6: [WhspR]  [Bld7]  [Bld8]               [------] [------]  [-----]
Row 7: [FstPs]  [----]  [----]                [------] [------]  [BldM3]
```

Notes:
- `[----]` = continuation of multi-row card above
- Buildings (Bld1-Bld8) each span 1.5 rows
- Quests (Quest1-4) each span 3 rows
- Building market (BldM1-3) each span 1.5 rows
- Top-row spaces (SunR, BackR, Garg) at half-column positions
- Side panel (columns 7-8) not shown — to the right of this grid

## Automated Test Coverage

No new pytest tests needed — this is a client-side rendering change. Verify via:
- `cd src && pytest` — existing tests pass (no regressions)
- `cd src && ruff check .` — code quality passes
- Manual visual verification per scenarios above
