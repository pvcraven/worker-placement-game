# Tasks: Client Disconnect & Reconnect

**Input**: Design documents from `/specs/028-client-reconnect/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Add reconnect credential infrastructure to NetworkClient that all user stories depend on

- [x] T001 Add reconnect credential attributes (`reconnect_game_code`, `reconnect_player_name`, `reconnect_slot_index`) and `set_reconnect_credentials()` / `clear_reconnect_credentials()` methods to `client/network_client.py`
- [x] T002 Add `window.slot_index = None` initialization alongside existing `window.game_code = None` in `client/main.py`

**Checkpoint**: Reconnect credential storage available — user story implementation can begin

---

## Phase 2: User Story 1 — Disconnected Player Reconnects Mid-Game (Priority: P1)

**Goal**: A disconnected player can rejoin an active game with the same name and game code, restoring full game state.

**Independent Test**: Start server + 2 clients, start game, close one client, reopen it, enter same name + game code, click Join. Verify the player rejoins with all state (resources, workers, cards, VP, turn position) intact.

### Server: Join-as-Reconnect

- [x] T003 [US1] In the `join_game` handler in `server/lobby.py`, detect when the target game is past LOBBY phase. If `player_name` matches a disconnected player, delegate to the existing `reconnect()` function with the matched player's `slot_index`. If no match, return an error ("Game already in progress").
- [x] T004 [US1] Add test for join-as-reconnect: join request for active game with matching disconnected player name succeeds and triggers reconnect flow in `tests/test_lobby.py`
- [x] T005 [P] [US1] Add test for join-as-reconnect rejection: join request for active game with non-matching name returns error in `tests/test_lobby.py`

### Client: Auto-Reconnect on Network Loss

- [x] T006 [US1] In `_connection_loop` in `client/network_client.py`, after WebSocket connects, check if reconnect credentials exist. If so, automatically enqueue a `ReconnectRequest` message (action: "reconnect", game_code, player_name, slot_index) to the outgoing queue.

### Client: Store Credentials for Reconnect

- [x] T007 [US1] In `client/views/menu_view.py`, when `game_created` response arrives, extract and store `slot_index` on `window.slot_index` from the response message. Also store it when `player_joined` response is processed.
- [x] T008 [US1] In `client/views/game_view.py`, when `game_started` is received and game state is set, extract own `slot_index` from the player entry matching `window.player_id` in the players list and store on `window.slot_index`. Then call `window.network.set_reconnect_credentials(window.game_code, window.player_name, window.slot_index)` to enable auto-reconnect.
- [x] T009 [US1] When returning to menu (e.g., game ends or player leaves), call `window.network.clear_reconnect_credentials()` to prevent stale reconnect attempts.

### Client: Handle Reconnect Response

- [x] T010 [US1] In `client/views/menu_view.py`, handle `state_sync` response in `on_update()`. When received, this means a join-as-reconnect succeeded — store the game state and transition to game view (similar to `game_started` flow), setting `window.player_id` from the matched player in the state.

**Checkpoint**: Disconnected players can reconnect via auto-reconnect (network loss) or manual rejoin (client restart). Full state is restored.

---

## Phase 3: User Story 2 — Remaining Players See Disconnected Status (Priority: P2)

**Goal**: Disconnected players' names appear in red text in the upper-left player list; names return to white on reconnect.

**Independent Test**: With 2 clients in a game, disconnect one. Verify the other client shows the disconnected player's name in red. Reconnect and verify it returns to white.

- [x] T011 [US2] In `_draw_player_list()` in `client/views/game_view.py`, read `p.get("is_connected", True)` for each player. Use `arcade.color.RED` when False, `arcade.color.WHITE` when True. Update the cached text object's `color` property each frame to handle transitions.
- [x] T012 [US2] In the `player_disconnected` message handler in `client/views/game_view.py`, update the matching player's `is_connected` field to `False` in the local `self.game_state["players"]` dict so the red text appears immediately without waiting for a full state sync.
- [x] T013 [US2] In the `player_reconnected` message handler in `client/views/game_view.py`, update the matching player's `is_connected` field to `True` in the local `self.game_state["players"]` dict so the white text restores immediately.

**Checkpoint**: Connected players see real-time red/white color changes in the player list based on connection status.

---

## Phase 4: User Story 3 — Reconnection Rejected for Mismatched Credentials (Priority: P3)

**Goal**: Invalid reconnect attempts (wrong name or game code) show a clear error message to the player.

**Independent Test**: With an active game, open a new client, enter a wrong name but correct game code, click Join. Verify a clear error message is displayed.

- [x] T014 [US3] In `client/views/menu_view.py`, ensure the existing `error` action handler in `on_update()` displays the error message from the server (e.g., "No game with that code." or "Game already in progress") in the status label so the player understands why reconnection failed.

**Checkpoint**: Invalid reconnection attempts show clear, user-readable error messages.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T015 Run `uv run pytest` and `ruff check .` — fix any failures or lint issues
- [x] T016 Manual end-to-end validation per `quickstart.md`: start server + 2 clients, play a game, disconnect one, verify red text, reconnect (both auto and manual restart), verify white text and full state restore

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies — start immediately
- **US1 (Phase 2)**: Depends on Phase 1 (needs credential storage)
- **US2 (Phase 3)**: No dependency on US1 — can start after Phase 1
- **US3 (Phase 4)**: No dependency on US1 or US2 — mostly verifying existing error handling
- **Polish (Phase 5)**: Depends on all user stories being complete

### Within User Story 1

```
T003 (server join-as-reconnect) ──┐
T004, T005 (tests) ──────────────┤── can run in parallel with T006-T009
T006 (auto-reconnect client) ────┘
T007 (store slot_index menu) ──> T008 (store slot_index game) ──> T009 (clear on exit)
T010 (handle state_sync in menu) depends on T003
```

### Parallel Opportunities

- T004 and T005 (tests) can run in parallel with each other
- US2 tasks (T011, T012, T013) can all start after Phase 1, independent of US1
- US3 (T014) can start immediately after Phase 1

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Foundational (T001, T002)
2. Complete Phase 2: User Story 1 (T003–T010)
3. **STOP and VALIDATE**: Test reconnect manually
4. Core reconnect functionality is usable

### Incremental Delivery

1. Foundation → credential storage ready
2. Add US1 → players can reconnect (MVP)
3. Add US2 → visual disconnect feedback (red/white text)
4. Add US3 → error messaging polish
5. Each story adds value without breaking previous stories

---

## Notes

- No new Pydantic message types needed — all exist in `shared/messages.py`
- Server already handles disconnect detection, state preservation, and reconnect matching
- The `is_connected` field is already included in game state synced to clients via `model_dump()`
- Config changes (turn_timeout → None, session preserve → 24h) are already complete
