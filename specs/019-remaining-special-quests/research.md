# Research: Remaining Special Quest Mechanics

## R1: How to handle "play intrigue from quest completion"

**Decision**: Create a new pending state (`pending_play_intrigue`) and a dedicated handler `handle_play_intrigue_from_quest()` that reuses `_resolve_intrigue_effect()`.

**Rationale**: The existing backstage flow (`handle_place_worker_backstage`) combines worker placement with intrigue play. We only need the intrigue resolution part. Extracting just `_resolve_intrigue_effect()` (which already exists as a pure function) and wrapping it in a new handler avoids touching the backstage flow. The pending state pattern matches existing `pending_quest_reward`, `pending_intrigue_target`, etc.

**Alternatives considered**:
- Reuse `handle_place_worker_backstage` directly: Rejected — it requires a backstage slot and worker placement, which don't apply here.
- Auto-play the "best" intrigue card: Rejected — spec says player chooses which card to play.

## R2: Opponent selection for "opponent gains coins"

**Decision**: In 2-player games, auto-grant to the single opponent. In 3+ player games, prompt the completing player to choose via a new `OpponentChoicePromptResponse`.

**Rationale**: Matches the spec exactly (FR-003, FR-004). The 2-player auto-grant avoids unnecessary UI prompts. The choice prompt follows the same pattern as `IntrigueTargetPromptResponse`.

**Alternatives considered**:
- Reuse IntrigueTargetPromptResponse: Rejected — different semantics (this is a gift, not an attack). Cleaner to have a dedicated message.
- All opponents gain coins: Rejected — spec says only one opponent receives them.

## R3: Dual building occupation model

**Decision**: Add `also_occupied_by: str | None = None` to ActionSpace rather than changing `occupied_by` to a list.

**Rationale**: Only one card in the entire game allows dual occupation, and it's limited to once per round. Changing `occupied_by` from `str | None` to `list[str]` would require updating every reference across the codebase (placement validation, owner bonus, round-end clearing, client rendering). Adding a single optional field is minimal-impact. At round end, both fields get cleared.

**Alternatives considered**:
- `occupied_by: list[str]`: Rejected — too many downstream changes for a single-card mechanic.
- Track only via a GameState flag without actual dual occupation: Rejected — the space genuinely needs both workers visible on it for correct rendering and owner bonus logic.

## R4: Worker recall — persistent or one-time?

**Decision**: Worker recall is a one-time completion reward, not a persistent per-round ability. When the player completes "Time Warp Remix", they immediately select one of their placed workers to recall. If no workers are placed, the step is skipped.

**Rationale**: User clarified this is a one-time effect at quest completion. This simplifies the implementation — no per-round tracking needed, no UI button to show each turn. It fits in the quest completion flow alongside other interactive rewards (play intrigue, choose opponent).

**Alternatives considered**:
- Persistent once-per-round recall: Rejected — user clarified this is wrong.
- Auto-recall (no player choice): Rejected — user wants the player to select which space to recall from.

## R5: Round-start resource choice timing

**Decision**: Apply round-start resource choice prompts in `_end_round()` after `state.current_round += 1`, after the bonus worker check, and after `RoundEndResponse` broadcast. Set a pending state (`pending_round_start_choices`) and prompt each eligible player in turn order. The first turn does not begin until all choices are resolved.

**Rationale**: The resource choice logically belongs to the new round. It must be interactive (player chooses), so we need a pending state to block turn advancement. This follows the same pattern as `pending_quest_reward` and `pending_resource_choice`. Each player is prompted sequentially in turn order to avoid race conditions.

**Alternatives considered**:
- New game phase (ROUND_START): Rejected — over-engineered for a single prompt.
- Auto-grant random resource: Rejected — user clarified that player chooses the resource.
- Prompt all players simultaneously: Rejected — sequential is simpler and avoids concurrent state issues.

## R6: Card data field naming

**Decision**: Use these field names on ContractCard:
- `reward_play_intrigue: int = 0` — how many intrigue cards to play on completion
- `reward_opponent_gains_coins: int = 0` — how many coins an opponent receives
- `reward_extra_worker: int = 0` — permanent workers granted
- `reward_choose_resource_per_round: bool = False` — choose a non-coin resource to gain each round
- `reward_recall_worker: bool = False` — on completion, recall one placed worker
- `reward_use_occupied_building: bool = False` — can use occupied buildings once per round

**Rationale**: Prefix all with `reward_` to group with existing reward fields (`reward_draw_intrigue`, `reward_draw_quests`, `reward_building`). Use int for countable effects, bool for toggles. Fields are read from contracts.json via Pydantic — no hard-coding of card IDs.
