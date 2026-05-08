# Feature Specification: Client Disconnect & Reconnect

**Feature Branch**: `028-client-reconnect`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Update the app to allow clients to disconnect and connect. If a client disconnects, let them reconnect. Client must have the same name and game code as when they logged in originally. If so, they pick back up where they left off. Disconnected clients appear as red text instead of white text in the upper left corner."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Disconnected Player Reconnects Mid-Game (Priority: P1)

A player loses their network connection or closes their client during an active game. When they relaunch the client and provide the same player name and game code, they rejoin the game in progress. Their full game state — resources, workers, cards, victory points, and position in the turn order — is restored exactly as it was when they disconnected.

**Why this priority**: This is the core value of the feature. Without reconnection, any network interruption forces a player to abandon the game entirely, ruining the experience for all participants.

**Independent Test**: A player in an active game closes their client, reopens it, enters the same name and game code, and verifies they see their full game state restored and can continue playing.

**Acceptance Scenarios**:

1. **Given** a player is in an active game and disconnects, **When** they reconnect with the same name and game code, **Then** they rejoin the game with all their state intact (resources, workers, cards, victory points, turn position).
2. **Given** a player disconnects during another player's turn, **When** they reconnect before their own turn arrives, **Then** the game continues seamlessly and they can take their turn normally.
3. **Given** a player disconnects during their own turn, **When** they reconnect, **Then** they resume their turn from where they left off.

---

### User Story 2 - Remaining Players See Disconnected Status (Priority: P2)

When a player disconnects, the other players in the game immediately see that player's name change from white to red text in the upper-left player list. This gives remaining players clear visual feedback that someone has dropped from the game.

**Why this priority**: Visual feedback about player connectivity is essential so remaining players understand why a player may not be taking their turn. Without this, players would be confused about delays.

**Independent Test**: While one player is in a game, a second player disconnects. The first player observes the second player's name turn red in the player list.

**Acceptance Scenarios**:

1. **Given** a multiplayer game is in progress, **When** a player disconnects, **Then** that player's name appears in red text (instead of white) in the upper-left player list for all remaining connected players.
2. **Given** a player's name is displayed in red (disconnected), **When** that player reconnects, **Then** their name returns to the normal white text color.

---

### User Story 3 - Reconnection Rejected for Mismatched Credentials (Priority: P3)

A player attempts to reconnect to a game but provides an incorrect name or game code. The system rejects the reconnection attempt and informs the player that their credentials do not match any active session.

**Why this priority**: Preventing unauthorized reconnection protects game integrity. Players should not be able to impersonate disconnected players or join games they were never part of.

**Independent Test**: A player attempts to reconnect with a valid game code but the wrong name, and receives a clear rejection message.

**Acceptance Scenarios**:

1. **Given** a game is in progress, **When** a player attempts to reconnect with the correct game code but a different name, **Then** the reconnection is rejected with a clear error message.
2. **Given** a game is in progress, **When** a player attempts to reconnect with the correct name but an incorrect game code, **Then** the reconnection is rejected with a clear error message.
3. **Given** no game exists for a game code, **When** a player attempts to reconnect, **Then** they are informed that no game was found.

---

### Edge Cases

- What happens if two clients try to reconnect as the same player simultaneously? Only the first connection should succeed; the second should be rejected or the first should be displaced.
- What happens if a disconnected player's turn comes up? The game should handle the turn timeout as it currently does (existing turn timeout behavior applies).
- What happens if all players disconnect? The game session should be preserved for a reasonable period, allowing any player to reconnect and resume.
- What happens if the game ends while a player is disconnected? The player should see the final results when they reconnect.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST detect when a client disconnects (network loss, client closure, or intentional exit).
- **FR-002**: The system MUST preserve the full game state for a disconnected player, including resources, workers, cards, victory points, and turn order position.
- **FR-003**: The system MUST allow a disconnected player to reconnect by providing the same player name and game code used when they originally joined.
- **FR-004**: Upon successful reconnection, the system MUST restore the player's complete game state so they can continue playing from where they left off.
- **FR-005**: The system MUST broadcast a player's connection status change (connected/disconnected) to all other players in the game.
- **FR-006**: The player list in the upper-left corner MUST display disconnected players' names in red text and connected players' names in white text.
- **FR-007**: When a reconnection attempt fails (wrong name or game code), the system MUST provide a clear error message to the player explaining why reconnection was rejected.
- **FR-008**: The system MUST NOT allow a new player to take over a disconnected player's slot — only the original player (matching name and game code) can reconnect.
- **FR-009**: The system MUST preserve game sessions for a reasonable period after all players disconnect, allowing reconnection.

### Key Entities

- **Player**: Represents a participant in a game. Has a connection status (connected/disconnected), display name, and association with a specific game via game code. Maintains all game state (resources, workers, cards, victory points) regardless of connection status.
- **Game Session**: An active game identified by a unique game code. Persists independently of individual player connections and remains available for reconnection as long as the session has not expired.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A disconnected player can reconnect and resume play within 10 seconds of re-entering their name and game code.
- **SC-002**: All connected players see a disconnected player's name change to red within 3 seconds of the disconnection event.
- **SC-003**: When a disconnected player reconnects, their name returns to white text for all players within 3 seconds.
- **SC-004**: 100% of game state (resources, workers, cards, victory points, turn position) is preserved and restored after reconnection.
- **SC-005**: Invalid reconnection attempts (wrong name or game code) are rejected with a user-understandable error message.

## Assumptions

- The existing turn timeout mechanism handles the case where a disconnected player's turn arrives before they reconnect.
- Game sessions are already preserved on the server when players disconnect (session cleanup only occurs after a configurable timeout period).
- Player name matching for reconnection is case-sensitive, consistent with how names are stored.
- A player who disconnects from the lobby (before the game starts) does not need reconnection — they can simply rejoin as a new player.
- The red/white color change applies only to the in-game player list in the upper-left corner, not to the lobby view.
