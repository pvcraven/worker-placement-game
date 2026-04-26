# Feature Specification: New Special Buildings

**Feature Branch**: `020-new-special-buildings`  
**Created**: 2026-04-26  
**Status**: Draft  
**Input**: User description: "Implement two new buildings, equivalents to Waterdeep's 'The Stone House' and 'Heroes' Garden'"

## User Scenarios & Testing

### User Story 1 - Royalty Collection Building (Priority: P1)

A player purchases a building (music-themed equivalent of "The Stone House") that rewards visitors with 1 coin for every player-purchased building tile currently in play on the board. Fixed board spaces do not count. The building owner receives 2 coins as their owner bonus whenever another player visits.

**Why this priority**: This building has a simple, self-contained mechanic — count buildings, award coins. No new interaction prompts or UI dialogs are needed. It is the simplest of the two to implement.

**Independent Test**: Purchase the building, place a worker on it, and verify the visitor receives coins equal to the number of buildings in play. Verify the owner receives 2 coins when another player visits.

**Acceptance Scenarios**:

1. **Given** a player owns this building and 5 buildings are in play, **When** another player places a worker on it, **Then** the visitor receives 5 coins and the owner receives 2 coins.
2. **Given** this building is purchased when 3 buildings are in play, **When** a 4th building is purchased later and then a player visits, **Then** the visitor receives 4 coins (count is dynamic, not fixed at purchase time).
3. **Given** a player owns and visits their own building when 6 buildings are in play, **Then** the visitor receives 6 coins but the owner bonus of 2 coins does NOT apply (owner bonuses never trigger on self-visits).
4. **Given** no other buildings have been purchased beyond this one, **When** a player visits, **Then** the visitor receives 1 coin (this building itself counts as a building in play).

---

### User Story 2 - Audition Showcase Building (Priority: P2)

A player purchases a building (music-themed equivalent of "Heroes' Garden") that lets the visitor take 1 face-up contract card from the available contracts. The visitor may then immediately complete that contract if they meet its requirements, earning 4 bonus victory points on top of the normal quest reward. If the visitor chooses not to complete the contract immediately (or cannot), the contract goes into their hand with no bonus — it can be completed later at normal value. The building owner scores 2 VP whenever another player visits.

**Why this priority**: This building introduces a contract-draw-and-complete pattern. The UI reuses the existing quest completion window — the drawn contract appears with "+4VP bonus" text if it is eligible for immediate completion. No new dialog is needed.

**Independent Test**: Purchase the building, place a worker on it, select a face-up contract, verify the option to complete immediately appears if requirements are met, and verify 4 bonus VP are awarded on immediate completion.

**Acceptance Scenarios**:

1. **Given** a player places a worker on this building and selects a face-up contract, and the drawn contract is completable, **When** the quest completion window opens, **Then** the drawn contract appears with "+4VP bonus" text underneath it. If the player completes it, they receive the normal quest reward plus 4 bonus VP.
2. **Given** a player places a worker on this building and selects a face-up contract they cannot afford, but they CAN complete a different quest in their hand, **When** the quest completion window opens, **Then** the drawn contract does NOT appear in the completion window (no bonus text shown), and the player may complete a different quest at normal value or skip.
3. **Given** a player places a worker on this building and selects a face-up contract, and the player cannot complete ANY quest (neither the drawn one nor any in hand), **When** the contract is drawn, **Then** the contract goes into their hand and the quest completion window is NOT shown (normal behavior when no quests are completable).
4. **Given** a player places a worker on this building and selects a contract they can afford, **When** they choose to skip quest completion (or complete a different quest instead), **Then** the drawn contract stays in their hand with no bonus. If completed later through normal quest completion, no bonus VP are awarded.
5. **Given** a player visits this building owned by another player, **When** the visit completes, **Then** the owner scores 2 VP.
6. **Given** a player has an uncompleted mandatory quest, **When** they visit this building and draw a contract, **Then** they cannot immediately complete a non-mandatory quest (mandatory quest must be completed first, per existing game rules).
7. **Given** the drawn contract has a building reward (reward_building), **When** the player completes it immediately, **Then** the building reward flow also triggers (pick a building from the market), followed by the 4 bonus VP.

---

### Edge Cases

- What happens when the building-count building is the only building in play? The visitor receives 1 coin (the building itself is in play).
- What happens when there are no face-up contracts available for the showcase building? The visitor receives no contract and no bonus VP opportunity. The visit still counts (worker is placed, owner bonus still triggers).
- What happens if the player draws a contract at the showcase building that has interactive rewards (resource choice, play intrigue, etc.) and completes it immediately? All interactive reward flows chain normally, with the 4 bonus VP added at the end.
- What happens if the visitor owns the showcase building? They get the contract draw + optional immediate completion, but the 2 VP owner bonus does NOT apply (owner bonuses never trigger on self-visits).

## Requirements

### Functional Requirements

- **FR-001**: The royalty collection building MUST award the visitor 1 coin for each player-purchased building currently in play on the board (including itself). Fixed board spaces (e.g., Sunset Strip, Vinyl Vault) do NOT count.
- **FR-002**: The royalty collection building MUST award its owner 2 coins when another player visits. The owner bonus does NOT apply when the owner visits their own building.
- **FR-003**: The building count for FR-001 MUST be calculated at the time of the visit, not at the time of purchase.
- **FR-004**: The audition showcase building MUST allow the visitor to select 1 face-up contract card from the available contracts.
- **FR-005**: After selecting a contract at the audition showcase building, the drawn contract is added to the player's hand. The existing quest completion window is then shown using normal quest completion rules. If the drawn contract is completable, it MUST appear in the quest completion window with "+4VP bonus" text displayed underneath it. If the drawn contract is NOT completable but other quests are, the drawn contract MUST NOT appear in the completion window and no bonus text is shown. If NO quests are completable, the quest completion window MUST NOT be shown (normal behavior).
- **FR-006**: If the player chooses to complete the contract immediately, the system MUST process all normal quest completion rewards (resources, VP, building grants, special rewards) plus add 4 bonus VP.
- **FR-007**: If the player cannot afford the selected contract, or chooses not to complete it (by completing a different quest or skipping), the drawn contract MUST remain in their hand with no bonus.
- **FR-008**: The audition showcase building owner MUST receive 2 VP when another player visits.
- **FR-009**: A replacement contract MUST be drawn from the contract deck to fill the empty face-up slot after a contract is taken from the showcase building.
- **FR-010**: Both buildings MUST cost 4 coins to purchase.
- **FR-011**: Both buildings MUST appear in the building market alongside existing buildings and follow all existing building purchase rules.
- **FR-012**: The immediate completion at the showcase building MUST respect mandatory quest rules — a player with an uncompleted mandatory quest cannot complete a non-mandatory quest.

### Key Entities

- **Building (Royalty Collection)**: A purchasable building with a dynamic coin reward based on total buildings in play. Cost: 4 coins. Visitor: 1 coin per building in play. Owner bonus: 2 coins.
- **Building (Audition Showcase)**: A purchasable building that grants contract selection plus optional immediate completion with bonus VP. Cost: 4 coins. Visitor: select 1 face-up contract, optionally complete immediately for +4 VP. Owner bonus: 2 VP.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Players can purchase both new buildings from the market for 4 coins each, following existing purchase flow.
- **SC-002**: Visiting the royalty collection building awards coins equal to the number of buildings currently in play, verified across different board states (1 building through 10+ buildings).
- **SC-003**: Visiting the audition showcase building allows contract selection and displays the immediate completion option when requirements are met.
- **SC-004**: Immediate completion at the audition showcase awards exactly 4 bonus VP on top of all normal quest rewards.
- **SC-005**: Building owner bonuses trigger correctly for both buildings (2 coins for royalty collection, 2 VP for audition showcase).
- **SC-006**: Both buildings are visually represented and interactable using existing building rendering patterns.

## Clarifications

### Session 2026-04-26

- Q: Does the royalty collection building owner get the owner bonus when visiting their own building? → A: No. Owner bonuses never trigger on self-visits, consistent with standard building rules.
- Q: How should the Audition Showcase immediate completion UI work? → A: Reuse the existing quest completion window. The drawn contract appears with "+4VP bonus" text if eligible for completion. If the drawn contract is not completable but others are, the drawn one is omitted and no bonus text shown. If no quests are completable, the window is not shown (normal behavior).
- Q: Does "buildings in play" include fixed board spaces or only player-purchased buildings? → A: Only player-purchased buildings count. Fixed board spaces are excluded.

## Assumptions

- Both buildings follow the existing building purchase, placement, and visit flows — no new board spaces or purchase mechanics are needed.
- The "buildings in play" count for the royalty collection building includes only player-purchased buildings placed on the board (including itself). Fixed board spaces are excluded.
- The audition showcase's "immediate completion" reuses the existing quest completion window. No new dialog is needed — the drawn contract appears alongside other completable quests, with "+4VP bonus" text when eligible.
- The 4 bonus VP for immediate completion at the audition showcase is a fixed value and does not scale.
- Building card images will need to be generated following the existing card image generation pipeline.
- Both buildings are added to the existing `buildings.json` configuration file alongside the current 20 buildings.
