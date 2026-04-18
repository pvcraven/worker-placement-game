# Research: Card Image Generator

**Feature**: Card Image Generator
**Date**: 2026-04-18

## Decision 1: Image Rendering Library

**Decision**: Pillow (PIL Fork)
**Rationale**: User explicitly requested Pillow. It's the standard Python image library, supports PNG with transparency, rounded rectangles via `ImageDraw.rounded_rectangle()`, and TrueType font rendering via `ImageFont.truetype()`.
**Alternatives considered**:
- Cairo/Pycairo — more powerful but heavier dependency, unnecessary for static card images
- ReportLab — PDF-focused, overkill for PNG generation
- Arcade — would require a running OpenGL context; not suitable for offline batch generation

## Decision 2: Reuse Existing Pydantic Models

**Decision**: Import `shared/card_models.py` and `server/models/config.py` directly
**Rationale**: All four card types (ContractCard, IntrigueCard, BuildingTile, ProducerCard) and their config loaders (ContractsConfig, IntrigueConfig, BuildingsConfig, ProducersConfig) already exist with full validation. Duplicating these models would violate DRY and risk drift.
**Alternatives considered**:
- Read JSON as raw dicts — violates Constitution Principle II (Pydantic Data Modeling)
- Create new models in card-generator/ — duplicates existing code

## Decision 3: Font Strategy

**Decision**: Use system font (Tahoma or Arial) via `ImageFont.truetype()`
**Rationale**: Matches the in-game rendering which uses Tahoma. System fonts avoid bundling font files. Pillow's `truetype()` can locate system-installed fonts by name on Windows.
**Alternatives considered**:
- Bundle a TTF file — adds repo bloat, licensing concerns
- Use Pillow's default bitmap font — poor quality at small sizes, no anti-aliasing

## Decision 4: Rounded Rectangle Approach

**Decision**: Use `ImageDraw.rounded_rectangle()` (Pillow 8.2+)
**Rationale**: Built-in Pillow method, no custom drawing code needed. Supports fill color and optional outline. Creates the parchment card shape on a transparent RGBA canvas.
**Alternatives considered**:
- Manual corner arcs with `pieslice()` — more code, same result
- Pre-made card template image — inflexible, harder to maintain

## Decision 5: Color Palette

**Decision**: Parchment background with dark brown text, genre-colored header bands for quest cards
**Rationale**: User clarified parchment background with rounded corners. Dark brown text (not pure black) gives a warmer, more thematic appearance on parchment. Genre header bands match the existing in-game CardRenderer colors.
**Colors**:
- Parchment fill: ~(235, 220, 185) or similar warm tan
- Dark text: ~(60, 40, 20) dark brown
- Genre bands: jazz=(40, 80, 120), pop=(120, 40, 80), soul=(80, 55, 120), funk=(120, 70, 10), rock=(100, 15, 25) — brighter than in-game dark variants since parchment provides contrast

## Decision 6: Python Path for Imports

**Decision**: Script adds project root to `sys.path` at startup
**Rationale**: The card generator lives in `card-generator/` but needs to import from `shared/` and `server/`. Adding the project root to sys.path is the simplest approach for a standalone script.
**Alternatives considered**:
- Make card-generator a proper package with pyproject.toml — over-engineered for a single script
- Copy/paste models — violates DRY
