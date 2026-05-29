# Server-Client Protocol: The Green Room

## Message Flow

### Happy Path: Play Intrigue + Select Quest

```
Client → Server: PlaceWorkerRequest { space_id: "the_green_room" }

Server validates:
  - Player has available workers
  - Space is unoccupied
  - Player has at least 1 intrigue card in hand

Server → All:    WorkerPlacedResponse { player_id, space_id: "the_green_room", reward_granted: {}, next_player_id: null }
Server → Player: IntriguePlayPromptResponse { intrigue_hand: [...] }

Client → Server: PlayIntrigueFromQuestRequest { intrigue_card_id: "..." }

Server resolves intrigue effect via _resolve_intrigue_effect()

  If effect is immediate (no target needed):
    Server → All: IntrigueEffectResolvedResponse { ... }
    (Server transitions to quest selection — client shows quest selection UI)

  If effect requires target selection:
    Server → Player: IntrigueTargetPromptResponse { eligible_targets: [...] }
    Client → Server: ChooseIntrigueTargetRequest { target_player_id: "..." }
    Server → All: IntrigueEffectResolvedResponse { ... }
    (Server transitions to quest selection)

Client → Server: SelectQuestCardRequest { card_id: "..." }
Server → All: QuestCardSelectedResponse { player_id, card_id, spot_number: 3, bonus_reward: {} }
Server → All: FaceUpQuestsUpdatedResponse { face_up_quests: [...] }
Server continues with _check_quest_completion() → _advance_turn()
```

### Cancel Path: Back Out Before Intrigue Play

```
Client → Server: PlaceWorkerRequest { space_id: "the_green_room" }
Server → All:    WorkerPlacedResponse { ... }
Server → Player: IntriguePlayPromptResponse { ... }

Client → Server: CancelPlacementRequest { }
Server unwinds placement via _unwind_placement()
Server → All: PlacementCancelledResponse { space_id: "the_green_room", ... }
```

### Rejection: No Intrigue Cards

```
Client → Server: PlaceWorkerRequest { space_id: "the_green_room" }
Server → Player: ErrorResponse { code: "INVALID_ACTION", message: "You need at least one intrigue card to use The Green Room." }
(Worker not placed, player can choose another space)
```
