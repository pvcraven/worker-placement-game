# Feature Specification: Multiplayer Worker Placement Game

**Feature Branch**: `001-worker-placement-game`  
**Created**: 2026-04-10  
**Status**: Draft  
**Input**: User description: "Build a Worker Placement Game similar to Lords of Waterdeep. It needs to be multiplayer, with a server and clients."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Host and Join a Game Lobby (Priority: P1)

A player creates a new game lobby, configuring basic settings such as the number of players (2-5). Other players join the lobby using a game code or lobby browser. Once all players are ready, the host starts the game. The server initializes the game board, deals secret quests to each player, assigns starting resources, and begins the first round.

**Why this priority**: Without lobby creation and joining, no multiplayer game can take place. This is the foundational multiplayer infrastructure.

**Independent Test**: Can be fully tested by one player creating a lobby and others joining it. Delivers the core multiplayer connectivity value even before gameplay is implemented.

**Acceptance Scenarios**:

1. **Given** a player is on the main menu, **When** they select "Create Game" and configure 3 player slots, **Then** a lobby is created and a joinable game code is displayed.
2. **Given** a lobby exists with available slots, **When** a second player enters the game code, **Then** they join the lobby and all players see the updated player list.
3. **Given** all players in the lobby have marked themselves as ready, **When** the host clicks "Start Game", **Then** the game initializes and all players see the game board.
4. **Given** a lobby is full (maximum players reached), **When** another player tries to join, **Then** they receive a "lobby full" message.

---

### User Story 2 - Place Workers and Collect Resources (Priority: P1)

During their turn, a player selects one of their available workers and places it on an unoccupied action space on the game board. The action space immediately grants the associated reward (resources such as Guitarists, Bass Players, Drummers, Singers, or Coins). The turn then passes to the next player. This continues until all players have placed all their workers, at which point the round ends.

**Why this priority**: Worker placement and resource collection are the core gameplay loop. Without this, there is no game.

**Independent Test**: Can be tested by placing workers on resource-granting spaces and verifying that players receive the correct resources. Delivers the fundamental game mechanic.

**Acceptance Scenarios**:

1. **Given** it is a player's turn and they have available workers, **When** they select a worker and place it on an unoccupied action space, **Then** the worker is placed, the player receives the space's reward, and the turn passes to the next player.
2. **Given** an action space is already occupied by another player's worker, **When** a player attempts to place a worker there, **Then** they are prevented from doing so and informed the space is occupied.
3. **Given** a player has placed all their workers for the round, **When** it would be their turn, **Then** they are skipped until all players have placed all workers.
4. **Given** all players have placed all their workers, **When** the last worker is placed, **Then** the Reassignment Phase begins (Garage workers are reassigned in slot order), after which all workers are returned to their owners and a new round begins.

---

### User Story 3 - Complete Quests to Score Victory Points (Priority: P1)

Each player holds a hand of quest cards. Each quest requires specific combinations of resources (e.g., 3 Guitarists and 2 Bass Players). When a player has accumulated the required resources, they may complete a quest on their turn (before or after placing a worker), spending the required resources and gaining Victory Points (and possibly bonus rewards). The player with the most Victory Points at the end of the final round wins.

**Why this priority**: Quests are the primary scoring mechanism and give purpose to resource collection. Without quests, resource gathering is meaningless.

**Independent Test**: Can be tested by giving a player the required resources for a quest and verifying they can complete it, spend resources, and gain Victory Points.

**Acceptance Scenarios**:

1. **Given** a player holds a quest requiring 3 Guitarists and 2 Coins, and the player has at least those resources, **When** they choose to complete the quest, **Then** the resources are deducted and Victory Points are awarded.
2. **Given** a player holds a quest but lacks the required resources, **When** they attempt to complete it, **Then** they are informed they do not have enough resources.
3. **Given** the final round has ended, **When** all end-of-game scoring is tallied, **Then** the player with the most Victory Points is declared the winner and all players see the final standings.

---

### User Story 4 - Acquire New Quests from the Talent Agency (Priority: P2)

Certain action spaces on the board (the "Talent Agency") allow a player to draw new quest cards from the available face-up quests or the quest deck. Players manage a hand of quests, choosing which to pursue based on their strategy and available resources.

**Why this priority**: Without quest acquisition, players are limited to their starting quests, severely limiting strategic depth and replayability.

**Independent Test**: Can be tested by a player placing a worker on a Talent Agency space and selecting from available face-up quest cards or drawing from the deck.

**Acceptance Scenarios**:

1. **Given** a player places a worker on a Talent Agency action space, **When** the action resolves, **Then** the player may choose one of the face-up quest cards or draw from the quest deck.
2. **Given** a player takes a face-up quest, **When** it is removed from the Talent Agency, **Then** a new quest card is drawn from the deck to replace it.

---

### User Story 5 - Play Intrigue Cards at The Garage and Reassign Workers (Priority: P2)

The Garage is a specialized action space with 3 numbered slots (1, 2, 3). When a player places a worker on a Garage slot, they must immediately play one Intrigue Card from their hand — the card's effect resolves instantly (e.g., gain resources, force an opponent to lose resources). A player must have at least one intrigue card to place a worker at The Garage.

After all players have placed all of their workers for the round, a Reassignment Phase occurs. Workers in The Garage are reassigned in slot order (1, 2, 3): each worker is moved to any unoccupied action space on the board, and the player receives that space's reward as a bonus action. Workers cannot be reassigned back to The Garage. Players may also complete one quest during their reassignment action.

**Why this priority**: The Garage is the primary mechanism for playing intrigue cards and provides critical strategic depth through the double-action mechanic. It creates meaningful tension around turn order, slot priority, and timing.

**Independent Test**: Can be tested by a player placing a worker on a Garage slot, playing an intrigue card, then verifying the reassignment phase triggers after all workers are placed and the worker is moved to a valid space.

**Acceptance Scenarios**:

1. **Given** a player has intrigue cards in hand, **When** they place a worker on an available Garage slot, **Then** they must immediately play one intrigue card and its effect is resolved.
2. **Given** a player has no intrigue cards, **When** they attempt to place a worker on The Garage, **Then** they are prevented from doing so and informed they need an intrigue card.
3. **Given** an intrigue card targets another player, **When** it is played, **Then** the targeted player sees a notification of the effect and their resources/state are updated accordingly.
4. **Given** all players have placed all workers and workers occupy Garage slots, **When** the Reassignment Phase begins, **Then** workers are reassigned in slot order (1, 2, 3) — each player places their Garage worker on any unoccupied action space and receives that space's reward.
5. **Given** a worker is being reassigned from The Garage, **When** the player chooses a destination, **Then** The Garage is not available as a reassignment target.
6. **Given** a player is reassigning a Garage worker and has the resources for a quest, **When** they complete the reassignment, **Then** they may also complete one quest during that action.

---

### User Story 6 - Construct Buildings for New Action Spaces (Priority: P3)

Players can purchase building tiles using Coins, placing them on empty building lots on the board. Constructed buildings create new action spaces available to all players. The building owner receives a bonus whenever another player uses their building.

**Why this priority**: Buildings add long-term strategic investment and board evolution, but are not essential for a functional core game loop.

**Independent Test**: Can be tested by a player purchasing a building, placing it on an empty lot, and verifying that other players can use the new space while the owner receives a bonus.

**Acceptance Scenarios**:

1. **Given** a player places a worker on the Builder's Hall and has enough Coins, **When** they purchase a building tile, **Then** the building is placed on an empty lot, the Coins is deducted, and the new action space becomes available.
2. **Given** a player uses an action space built by another player, **When** the action resolves, **Then** the building owner receives a bonus reward (as defined on the building tile).
3. **Given** no empty building lots remain, **When** a player attempts to construct a building, **Then** they are informed no lots are available.

---

### User Story 7 - Gain Additional Worker at Round 5 (Priority: P2)

At the start of round 5, all players automatically receive one additional worker. This increases each player's actions per round for the second half of the game, accelerating the pace as the game approaches its conclusion.

**Why this priority**: The mid-game worker increase is a core pacing mechanic that changes the strategic landscape for the final 4 rounds. It is not player-driven (no action space needed) but must be correctly timed and applied.

**Independent Test**: Can be tested by advancing the game to round 5 and verifying all players receive one additional worker that is available for placement that round.

**Acceptance Scenarios**:

1. **Given** round 4 has ended, **When** round 5 begins, **Then** all players automatically gain one additional worker added to their available pool for that round.
2. **Given** a game is in progress at round 4 or earlier, **When** a player checks their worker count, **Then** it matches their starting count (no early bonus worker).

---

### User Story 8 - Reconnect to an In-Progress Game (Priority: P2)

If a player loses their connection during a game, they can reconnect and resume play from where they left off. The game state is preserved on the server, and the reconnecting player's view is synchronized.

**Why this priority**: Network reliability is essential for multiplayer games. Without reconnection, a single dropped connection ruins the experience for all players.

**Independent Test**: Can be tested by simulating a player disconnect, then reconnecting and verifying the game state is correctly restored.

**Acceptance Scenarios**:

1. **Given** a player disconnects mid-game, **When** they reconnect using the same game code and select their player slot by display name, **Then** they rejoin the game with the current state fully synchronized.
2. **Given** a player is disconnected and it becomes their turn, **When** a timeout period elapses, **Then** their turn is automatically skipped until they reconnect or a configurable number of turns are missed.
3. **Given** a player has been disconnected for an extended period, **When** the remaining players agree, **Then** the disconnected player may be replaced by a simple AI or removed from the game.

---

### Edge Cases

- What happens when a player disconnects during their worker placement action?
  - The partially completed action is rolled back, and the turn timer restarts when they reconnect.
- What happens when the host disconnects?
  - The server continues running the game. Host privileges transfer to the next player.
- What happens if all players disconnect?
  - The game state is preserved on the server for a configurable timeout period (default: 30 minutes), after which the game is abandoned.
- What happens when a player tries to complete a quest during another player's turn?
  - Quest completion is only allowed during the active player's own turn phase.
- What happens when there are no more quests in the deck?
  - The face-up quest slots that are empty remain empty. Players must work with their existing hand.
- What happens when two players reach the same Victory Point total?
  - The tiebreaker is determined by: (1) most Coins remaining, then (2) most total resources remaining, then (3) most quests completed.
- What happens if all 3 Garage slots are occupied and a player wants to play an intrigue card?
  - They cannot place a worker at The Garage and must choose a different action space.
- What happens during reassignment if all other action spaces are occupied?
  - The Garage worker is returned to the player without taking a bonus action (no valid destination).
- What happens if a player disconnects during the Reassignment Phase?
  - Their Garage worker is returned without reassignment. The remaining reassignments proceed in slot order.

## Clarifications

### Session 2026-04-10

- Q: How should the game client handle window resizing? → A: The game must resize responsively with the client window, support fullscreen expansion, and shrink down to a defined minimum size.
- Q: How are players identified for reconnection and lobby membership? → A: Anonymous — display name only, no persistent identity or accounts. Reconnection relies on the game code and player slot, not authenticated identity.
- Q: How many workers does each player start with, and what are the starting resources? → A: Starting workers scale by player count: 2 players = 4 workers, 3 players = 3 workers, 4 players = 2 workers, 5 players = 2 workers. All players start with 0 resources, 0 Coins, and 0 quests.
- Q: Can a player complete multiple quests in a single turn? → A: No, one quest per turn maximum.
- Q: How many quest types and total quest cards? → A: 5 quest types (Jazz, Rock, Soul, Funk, Pop) with approximately 25 total quest cards.
- Q: What can players do when it is not their turn? → A: Players can freely browse their own quests, resources, and the board but cannot take actions until their turn.
- Q: How should game content (cards, board items) be managed for balance iteration? → A: All game content must be defined in external configuration files (e.g., JSON or another text format) so that names, resource costs, rewards, and other attributes can be updated without code changes.
- Q: How many quest cards, building tiles, and what quest structure? → A: 60 quest cards (34 easier quests worth ≤9 VP, 26 harder quests worth ≥10 VP), 24 building tiles. 5 quest types: Jazz, Pop, Soul, Funk, Rock. Plot Quests are a special category that remain in play after completion, granting permanent ongoing benefits (e.g., +2 VP per Rock quest completed). Plot Quests will be implemented in a later phase but the architecture must accommodate them from the start.
- Q: How many intrigue cards and Producer cards? → A: 50 intrigue cards (no mandatory quest mechanic — unlike Lords of Waterdeep). ~11 Producer cards.
- Q: How does worker recruitment work? → A: No action-space-based recruitment. Worker counts are fixed and equal for all players. At the start of round 5, every player automatically gains one additional worker for the remainder of the game.
- Q: How many face-up quests in the Talent Agency? → A: 5 face-up quest cards visible at all times, refilled from the deck when taken.
- Q: Should the server validate configuration files on startup? → A: Yes — validate structure and required fields on load; warn on suspicious values (e.g., zero-cost quests) but allow them for playtesting flexibility.
- Q: What is the game's theme? → A: Music industry theme. Players are Record Labels assembling bands. Resources are musicians: Singers (purple), Guitarists (red), Drummers (white), Bass Players (black), and Coins (gold). Quests are Contracts (assembling bands). Quest types are music genres: Jazz, Pop, Soul, Funk, Rock. Lord cards become Producer cards. The board locations use music-themed names.
- Q: What are the starting board locations? → A: 7 basic permanent locations (The Three Cups: 2 Coins; The Grinning Lion Pub: 2 Bass Players; The Arena: 2 Guitarists; The Pool of Tears: 2 Singers; The Cathedral: 2 Drummers; Cliffwatch Inn: 3 action spots for contracts/intrigue cards; Builder's Hall: buy buildings), plus Castle Waterdeep (gain first-player marker + 1 intrigue card), plus The Garage (3 intrigue card slots with reassignment).
- Q: What are example intrigue card themes? → A: Music industry themed — examples include "Private Plane" (gain resources), "We Are The World Concert" (all-player event), "Extra Recording Time" (bonus action/resources), "Award Shows" (VP bonus), "Roadies Go On Strike" (opponent loses resources). The 50 intrigue cards should use creative music industry scenarios for their effects.
- Q: What theme should building tiles use? → A: Famous recording studios and music venues (e.g., "First Avenue" in Minneapolis, "Abbey Road Studios", "The Troubadour"). Building tiles represent iconic music locations that become new action spaces.
- Q: How does The Garage (intrigue card) action space work? → A: The Garage has 3 numbered slots (1, 2, 3) where workers can be placed. Placing a worker requires playing an intrigue card immediately (must have one in hand). After all players have placed all workers, a Reassignment Phase occurs: workers in The Garage are reassigned in slot order (1, 2, 3) to any unoccupied action space on the board (but not back to The Garage). Players may complete a quest during reassignment. This gives Garage users a "double action" — play an intrigue card, then take a second action at another space.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support 2 to 5 players in a single game session.
- **FR-001a**: System MUST assign starting workers based on player count: 4 workers for 2 players, 3 workers for 3 players, 2 workers for 4-5 players.
- **FR-001b**: System MUST start each player with 0 resources (Guitarists, Bass Players, Drummers, Singers), 0 Coins, and 0 quest cards.
- **FR-002**: System MUST provide a game lobby where a host can create a game and other players can join using a game code.
- **FR-003**: System MUST enforce turn-based worker placement where each player places one worker per turn in rotation.
- **FR-004**: System MUST prevent a player from placing a worker on an action space already occupied by another player's worker in the current round. Exception: The Garage has 3 distinct numbered slots that can each be occupied by different players' workers.
- **FR-005**: System MUST track four resource types (Guitarists, Bass Players, Drummers, Singers) and one currency (Coins) per player.
- **FR-006**: System MUST support quest cards with defined resource costs and Victory Point rewards. The game includes 5 quest types (Jazz, Pop, Soul, Funk, Rock) with 60 total quest cards: 34 easier quests (≤9 VP) and 26 harder quests (≥10 VP).
- **FR-006a**: System MUST support Plot Quests — a quest subtype that, once completed, remains in the player's area and provides permanent ongoing benefits for the remainder of the game (e.g., bonus VP per quest of a specific type completed afterward). Plot Quests are deferred to a later implementation phase, but the data model and configuration format must accommodate them from the start.
- **FR-007**: System MUST allow a player to complete a quest when they have the required resources, deducting the resources and awarding Victory Points. Limited to one quest completion per turn.
- **FR-008**: System MUST return all workers to their owners at the end of each round, after the Reassignment Phase (if any Garage workers were placed) has completed.
- **FR-009**: System MUST run for a fixed number of rounds (8 rounds), after which end-of-game scoring determines the winner.
- **FR-010**: System MUST assign each player a secret Producer card at the start of the game that grants bonus Victory Points at end-of-game for specific quest types completed.
- **FR-011**: System MUST support Intrigue Cards (50 total) that can be played for tactical effects targeting self or other players. The game does not include mandatory quest cards — intrigue effects are limited to resource manipulation, bonus grants, and other tactical advantages. Intrigue cards are played exclusively at The Garage action space.
- **FR-011a**: The Garage MUST have 3 numbered slots (1, 2, 3). Placing a worker on a Garage slot requires the player to immediately play one intrigue card from their hand. Players without intrigue cards cannot place workers at The Garage.
- **FR-011b**: System MUST implement a Reassignment Phase after all players have placed all workers for the round. Workers in The Garage are reassigned in slot order (1, 2, 3) to any unoccupied action space on the board (excluding The Garage). The player receives the destination space's reward. Players may complete one quest during their reassignment action.
- **FR-011c**: System MUST prevent reassignment of Garage workers back to The Garage.
- **FR-012**: System MUST allow construction of new building action spaces that persist for the remainder of the game. The game includes 24 building tiles.
- **FR-013**: System MUST grant the building owner a bonus when another player uses their building's action space.
- **FR-014**: System MUST automatically grant all players one additional worker at the start of round 5. Worker counts are always equal across all players (no action-space-based recruitment).
- **FR-015**: System MUST maintain authoritative game state on the server, with clients displaying a synchronized view.
- **FR-016**: System MUST support player reconnection to in-progress games without data loss.
- **FR-017**: System MUST handle turn timeouts for disconnected players (configurable, default 60 seconds per turn).
- **FR-018**: System MUST display a visible game log showing all actions taken by all players.
- **FR-019**: System MUST show each player their own resources, quests, and intrigue cards while hiding other players' hidden information (hand contents, secret Producer card).
- **FR-025**: System MUST allow players to browse their own quests, resources, and the game board at any time, including when it is not their turn. Action-taking (placing workers, completing quests, playing cards) is restricted to the active player's turn only.
- **FR-020**: System MUST provide a face-up quest display (Talent Agency) showing 5 quest cards at all times, with automatic refill from the deck when a card is taken.
- **FR-021**: System MUST calculate and display final scores including Producer card bonuses at end of game.
- **FR-022**: System MUST validate all player actions server-side to prevent cheating.
- **FR-023**: System MUST render the game board and UI responsively, scaling to fit the client window size including fullscreen mode.
- **FR-024**: System MUST enforce a minimum display size below which the UI does not shrink further (scrollbars or a "window too small" message may appear instead).
- **FR-026**: System MUST load all game content (quest cards, intrigue cards, building tiles, Producer cards, action spaces) from external configuration files rather than hardcoding them, enabling balance changes without code modifications.
- **FR-027**: Configuration files MUST define, at minimum: item name, resource costs, rewards (Victory Points, resources, Coins), and any special effects or conditions for each content type.
- **FR-028**: System MUST validate configuration file structure and required fields on startup, rejecting files with missing or malformed required fields. Suspicious but valid values (e.g., zero-cost contracts, unusually high rewards) MUST produce warnings but not prevent loading.
- **FR-029**: The game board MUST include the following permanent action spaces: The Three Cups (gain 2 Coins), The Grinning Lion Pub (gain 2 Bass Players), The Arena (gain 2 Guitarists), The Pool of Tears (gain 2 Singers), The Cathedral (gain 2 Drummers), Cliffwatch Inn (3 distinct action spots for acquiring contracts or intrigue cards), and Builder's Hall (purchase building tiles).
- **FR-030**: The game board MUST include Castle Waterdeep, which grants the first-player marker (determining turn order for the next round) and 1 intrigue card.
- **FR-031**: The game board MUST include The Garage with 3 numbered slots for intrigue card play and worker reassignment (as defined in FR-011a/b/c).
- **FR-032**: System MUST track and assign a first-player marker. The player who places a worker on Castle Waterdeep gains the first-player marker and goes first in the next round's turn order.

### Key Entities

- **Record Label** (Player): Represents a connected participant. Identified by a label name chosen at join time (no account or authentication required). Has a color/identity, a set of agents (workers), musician resources (Guitarists/red, Bass Players/black, Drummers/white, Singers/purple) and Coins (gold), a hand of contract cards, a hand of intrigue cards, a secret Producer card, completed contracts, and a Victory Point total.
- **Worker**: A token belonging to a player that can be placed on one action space per round. Returned to the player at end of round. Starting count varies by player count (4/3/2/2 for 2/3/4/5 players respectively). All players gain one additional worker at the start of round 5.
- **Action Space**: A location on the game board where a worker can be placed. Grants specific rewards or abilities. Some are permanent (board defaults), others are player-constructed buildings.
- **Contract Card** (Quest): Represents a band to assemble. Defines required musicians (resource costs) and Victory Point rewards. Belongs to one of 5 music genres (Jazz, Pop, Soul, Funk, Rock). 60 total cards in the deck: 34 easier (≤9 VP) and 26 harder (≥10 VP). May grant bonus rewards on completion. A subset are Plot Contracts that remain in play after completion, providing permanent ongoing benefits (deferred to later phase but supported in data model).
- **Building Tile**: A purchasable tile themed as a famous recording studio or music venue (e.g., "First Avenue", "Abbey Road Studios", "The Troubadour"). Creates a new action space when placed on an empty lot. 24 tiles in the game. Defines the action reward and the owner's bonus.
- **Intrigue Card**: A music-industry-themed card with a tactical effect, played at The Garage action space. 50 total cards. Examples: "Private Plane" (gain resources), "We Are The World Concert" (multi-player event), "Extra Recording Time" (bonus resources), "Award Shows" (VP bonus), "Roadies Go On Strike" (opponent loses resources). Effects include resource gain, resource theft, and other tactical advantages. No mandatory quest mechanic.
- **The Garage**: A specialized action space with 3 numbered slots. Workers placed here require an intrigue card to be played immediately. During the Reassignment Phase (after all workers are placed), Garage workers are reassigned in slot order to other unoccupied action spaces for a bonus action.
- **Producer Card**: A secret music producer identity card dealt at game start. ~11 total cards. Awards end-of-game bonus Victory Points based on the genres of contracts completed (e.g., a producer specializing in Rock and Funk genres).
- **Game Board**: The shared play area containing all permanent action spaces (The Three Cups, Grinning Lion Pub, The Arena, Pool of Tears, The Cathedral, Cliffwatch Inn, Builder's Hall, Castle Waterdeep, Garage), building lots for constructed venues, contract display, and player status displays.
- **First-Player Marker**: Gained by placing a worker on Castle Waterdeep. Determines which player goes first in the next round's turn order.
- **Game Session**: The server-side container for a complete game, tracking all state across rounds, managing turns, and enforcing rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can create a lobby and have all players joined and ready within 2 minutes.
- **SC-002**: A complete 8-round game with 4 players can be finished within 60-90 minutes.
- **SC-003**: All player actions (place worker, complete quest, play card) are reflected on all clients within 2 seconds.
- **SC-004**: A disconnected player can reconnect and resume play within 10 seconds of re-establishing connection.
- **SC-005**: The game correctly enforces all placement and quest completion rules with zero exploitable loopholes (server-side validation).
- **SC-006**: Players can understand the game interface and begin placing workers without external instructions (intuitive board layout and clear visual feedback).
- **SC-007**: The system supports at least 10 concurrent game sessions without performance degradation.
- **SC-008**: End-of-game scoring including Producer card bonuses is calculated correctly 100% of the time.
- **SC-009**: The game board and UI remain fully usable and visually coherent at any window size from the minimum threshold up to fullscreen.

## Assumptions

- Players have a stable internet connection suitable for real-time multiplayer (low-latency is preferred but the game is turn-based so brief latency spikes are tolerable).
- The game will be played via a visual client (web browser or desktop application); the specification does not prescribe the technology.
- The game board layout, quest cards, intrigue cards, Producer cards, and building tiles will be pre-designed content defined in external configuration files bundled with the game. Content is author-edited (not user-generated at runtime) but easily modifiable for balance iteration.
- The game uses a fixed board layout with 9 permanent action locations (7 basic + Castle Waterdeep + Garage), plus building lots for player-constructed venues.
- No real-money transactions or monetization are in scope.
- AI opponents are out of scope for the initial version (except as optional replacement for disconnected players).
- Mobile device support is out of scope for the initial version.
- Voice/text chat between players is out of scope; players are expected to use external communication tools.
- The game uses a music industry theme: players are Record Labels, quests are Contracts (assembling bands), resources are musicians (Singers/purple, Guitarists/red, Drummers/white, Bass Players/black) and Coins (gold). Quest types are music genres (Jazz, Pop, Soul, Funk, Rock). Producer Cards replace the fantasy "Lord" concept.
