# Implementation Plan: Intrigue Card Animation

**Branch**: `032-intrigue-card-animation` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/032-intrigue-card-animation/spec.md`

## Summary

Add full-size face-down intrigue card image generation and three-phase fly-in/fly-out animations for intrigue card draw and play events, matching the existing quest card animation pattern. Draw animations show face-up to the drawer and face-down to opponents; play animations show face-up to everyone. All animations integrate with the event queue and play a card drag sound.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pillow (PIL), Pydantic v2, websockets
**Storage**: In-memory game state; JSON config; PNG image files
**Testing**: pytest + ruff
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Desktop multiplayer game (client-server)
**Performance Goals**: 60 fps rendering, animations must not block the render loop
**Constraints**: Animations must integrate with the existing event queue; server must remain stateless between messages
**Scale/Scope**: 2-4 player local network games

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | **PASS** | Animations use sprites via AnimationManager; no primitive draw calls |
| II. Pydantic Data Modeling | **PASS** | Modified `IntrigueEffectResolvedResponse` is a Pydantic BaseModel |
| III. Client-Server Separation | **PASS** | All animation logic is client-side; server only adds fields to existing broadcast |
| IV. Test-Driven Game Logic | **PASS** | Server message changes tested via pytest; animation is client-side visual |
| V. Simplicity First | **PASS** | Reuses existing AnimationManager, event queue, and card sound; no new abstractions |
| VI. Server-Authoritative Message Protocol | **PASS** | Modified response follows existing broadcast pattern; new fields are additive |
| VII. Config-Driven Game Content | **N/A** | No new game content types |
| VIII. Pending State | **N/A** | No new multi-step interactions |
| IX. Cancel/Unwind | **N/A** | Animations are non-interactive and non-cancellable |
| X. Post-Action Turn Flow | **N/A** | No changes to turn advancement |

## Project Structure

### Documentation (this feature)

```text
specs/032-intrigue-card-animation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research findings
├── data-model.md        # Phase 1 data model changes
├── quickstart.md        # Phase 1 quickstart guide
├── contracts/           # Phase 1 message contracts
│   └── messages.md      # Modified message types
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
card-generator/
  generate_cards.py          # MODIFY: add generate_intrigue_back() function

shared/
  messages.py                # MODIFY: add fields to IntrigueEffectResolvedResponse

server/
  game_engine.py             # MODIFY: include card details in effect resolution broadcasts

client/
  views/
    game_view.py             # MODIFY: add intrigue draw/play animation functions
  assets/
    card_images/
      intrigue/
        intrigue_back.png    # NEW: generated face-down card image (400×500)
    sounds/
      card1.mp3              # EXISTING: card drag sound

tests/                       # MODIFY: add/update tests for server message changes
```

**Structure Decision**: All changes are modifications to existing files in the established project structure. One new generated asset (`intrigue_back.png`) is added to the existing intrigue card images directory.

## Phase 0: Research

See [research.md](research.md) for full findings. Key decisions:

- **R1**: Full-size face-down image at 400×500 using existing icon visual pattern (scaled up)
- **R2**: Quest draw animation hooks into `_on_quest_completed()` using existing `drawn_intrigue` data
- **R3**: Backstage draw animation hooks into backstage handler using existing `intrigue_card` data
- **R4**: Play animation requires adding `intrigue_card_id`/`intrigue_card_name` to `IntrigueEffectResolvedResponse`
- **R5**: Animation timing matches quest card pattern: 0.5s entry + 2.0s pause + 0.75s exit
- **R6**: Sound reuses `self._card_sound` (card1.mp3) on entry phase
- **R7**: Event queue integration via `AnimationEvent` — one per card, FIFO sequencing
- **R8**: Face-up sprites from `intrigue/{card_id}.png`, face-down from `intrigue/intrigue_back.png`

## Phase 1: Design

See [data-model.md](data-model.md) and [contracts/messages.md](contracts/messages.md).

### Server Changes

**`shared/messages.py`** — `IntrigueEffectResolvedResponse`:
- Add `intrigue_card_id: str = ""`
- Add `intrigue_card_name: str = ""`

**`server/game_engine.py`**:
- In `handle_choose_intrigue_target()`: Include card ID and name when broadcasting `IntrigueEffectResolvedResponse`
- In `handle_play_intrigue_from_quest()`: For non-targeting effects, broadcast `IntrigueEffectResolvedResponse` to all clients (currently only advances turn without broadcasting)

### Card Generator Changes

**`card-generator/generate_cards.py`**:
- Add `generate_intrigue_back()` function producing `intrigue_back.png` at 400×500 px
- Visual: black border → white border → dark gray (60,60,60) fill → centered "I" in parchment (235,220,185)
- Use proportionally scaled border widths and font size relative to full card dimensions
- Call from `main()` alongside existing generators

### Client Animation Changes

**`client/views/game_view.py`**:

**New function: `_start_intrigue_draw_animation(card_id, pid, event)`**
- If `pid == local_player_id`: load face-up sprite from `intrigue/{card_id}.png`
- Else: load face-down sprite from `intrigue/intrigue_back.png`
- Three-phase animation chain:
  1. Entry: `(window.width - 100, 100)` → `(window.width/2, window.height/2)`, 0.5s, SINE, scale→scale*2, sound=card_sound
  2. Pause: center→center, 2.0s, LINEAR, scale stays
  3. Exit: center → `_player_marker_positions[pid]`, 0.75s, QUAD_IN, scale→original, on_complete sets event.done

**New function: `_start_intrigue_play_animation(card_id, pid, event)`**
- Always load face-up sprite from `intrigue/{card_id}.png`
- Three-phase animation chain:
  1. Entry: `_player_marker_positions[pid]` → center, 0.5s, SINE, scale→scale*2, sound=card_sound
  2. Pause: center→center, 2.0s, LINEAR
  3. Exit: center → `(window.width - 100, 100)`, 0.75s, QUAD_IN, scale→original, on_complete sets event.done

**Modified: `_on_quest_completed()`**
- After processing drawn intrigue cards, for each card in `drawn_intrigue`:
  - Create `AnimationEvent` with setup calling `_start_intrigue_draw_animation(card["id"], pid, event)`
  - Enqueue the event

**Modified: backstage handler**
- After receiving `WorkerPlacedBackstageResponse`, queue draw animation for the intrigue card

**Modified: `_on_intrigue_effect_resolved()`**
- Before processing the effect, queue play animation using `intrigue_card_id` from the message

### Post-Design Constitution Re-Check

| Principle | Status |
|-----------|--------|
| I. Arcade Rendering Standards | **PASS** — sprites only, no draw calls |
| II. Pydantic Data Modeling | **PASS** — message fields are Pydantic |
| III. Client-Server Separation | **PASS** — animations client-only |
| V. Simplicity First | **PASS** — reuses all existing infrastructure |
| VI. Server-Authoritative Message Protocol | **PASS** — additive fields on existing broadcast |
