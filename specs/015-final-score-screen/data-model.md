# Data Model: Final Score Screen

**Feature**: 015-final-score-screen
**Date**: 2026-04-21

## Modified Entities

### FinalPlayerScore (shared/messages.py)

Existing Pydantic model — updated fields for spec alignment.

| Field              | Type              | Change     | Description                                    |
|--------------------|-------------------|------------|------------------------------------------------|
| player_id          | str               | unchanged  | Unique player identifier                       |
| player_name        | str               | unchanged  | Display name of the player                     |
| game_vp            | int               | renamed    | VP from completed quests (was `base_vp`)       |
| genre_bonus_vp     | int               | renamed    | VP from producer genre matches (was `producer_bonus`) |
| resource_vp        | int               | **new**    | VP from leftover resources (musicians + coin pairs) |
| producer_card      | dict              | unchanged  | Producer card data for display                 |
| total_vp           | int               | unchanged  | game_vp + genre_bonus_vp + resource_vp         |
| rank               | int               | unchanged  | 1-based placement rank                         |

**Calculation rules**:
- `game_vp` = sum of `victory_points` from all `completed_contracts`
- `genre_bonus_vp` = count of completed contracts whose `genre` is in `producer_card.bonus_genres` multiplied by `producer_card.bonus_vp_per_contract` (default 4). Zero if no producer card.
- `resource_vp` = `guitarists + bass_players + drummers + singers + floor(coins / 2)`
- `total_vp` = `game_vp + genre_bonus_vp + resource_vp`

### GameOverResponse (shared/messages.py)

No structural changes. Contains `final_scores: list[FinalPlayerScore]` and `tiebreaker_applied: bool`.

## Existing Entities (Unchanged)

### Player (server/models/game.py)

Used as data source for VP calculations. Relevant fields:
- `victory_points: int` — accumulated game VP
- `completed_contracts: list[ContractCard]` — quests with genre and VP
- `producer_card: ProducerCard | None` — genre bonus source
- `resources: PlayerResources` — guitarists, bass_players, drummers, singers, coins

### ProducerCard (shared/card_models.py)

- `bonus_genres: list[Genre]` — genres that earn bonus VP
- `bonus_vp_per_contract: int` — VP per matching quest (default 4)

### ContractCard (shared/card_models.py)

- `genre: Genre` — quest genre for producer matching
- `victory_points: int` — base VP earned on completion

### PlayerResources (server/models/game.py)

- `guitarists: int`, `bass_players: int`, `drummers: int`, `singers: int`, `coins: int`

## Client-Side Display Data

During gameplay (manual toggle), the client constructs a partial score breakdown from game state:

| Data Point      | Own Player | Opponents           |
|-----------------|------------|---------------------|
| Game VP         | Available  | Available           |
| Genre Bonus VP  | Available  | Hidden (producer card not visible) |
| Resource VP     | Available  | Available           |
| Total VP        | Complete   | Partial (excludes genre bonus) |

During game-over, the server provides authoritative `FinalPlayerScore` for all players with all fields populated.
