"""Shared Pydantic message models for WebSocket communication.

All messages use a discriminated union on the ``action`` field.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

# ---------------------------------------------------------------------------
# Client -> Server messages
# ---------------------------------------------------------------------------


class CreateGameRequest(BaseModel):
    action: Literal["create_game"] = "create_game"
    player_name: str = Field(min_length=1, max_length=30)
    max_players: int = Field(ge=2, le=5)


class JoinGameRequest(BaseModel):
    action: Literal["join_game"] = "join_game"
    game_code: str
    player_name: str = Field(min_length=1, max_length=30)


class PlayerReadyRequest(BaseModel):
    action: Literal["player_ready"] = "player_ready"
    ready: bool


class StartGameRequest(BaseModel):
    action: Literal["start_game"] = "start_game"


class PlaceWorkerRequest(BaseModel):
    action: Literal["place_worker"] = "place_worker"
    space_id: str


class PlaceWorkerBackstageRequest(BaseModel):
    action: Literal["place_worker_backstage"] = "place_worker_backstage"
    slot_number: int = Field(ge=1, le=3)
    intrigue_card_id: str


class SelectQuestCardRequest(BaseModel):
    action: Literal["select_quest_card"] = "select_quest_card"
    card_id: str


class CompleteQuestRequest(BaseModel):
    action: Literal["complete_quest"] = "complete_quest"
    contract_id: str


class AcquireContractRequest(BaseModel):
    action: Literal["acquire_contract"] = "acquire_contract"
    contract_id: str
    source: Literal["face_up", "deck"] = "face_up"


class AcquireIntrigueRequest(BaseModel):
    action: Literal["acquire_intrigue"] = "acquire_intrigue"


class PurchaseBuildingRequest(BaseModel):
    action: Literal["purchase_building"] = "purchase_building"
    building_id: str


class CancelPurchaseBuildingRequest(BaseModel):
    action: Literal["cancel_purchase_building"] = "cancel_purchase_building"


class CancelQuestSelectionRequest(BaseModel):
    action: Literal["cancel_quest_selection"] = "cancel_quest_selection"


class CancelIntrigueTargetRequest(BaseModel):
    action: Literal["cancel_intrigue_target"] = "cancel_intrigue_target"


class SkipQuestCompletionRequest(BaseModel):
    action: Literal["skip_quest_completion"] = "skip_quest_completion"


class ReassignWorkerRequest(BaseModel):
    action: Literal["reassign_worker"] = "reassign_worker"
    slot_number: int = Field(ge=1, le=3)
    target_space_id: str


class ChooseIntrigueTargetRequest(BaseModel):
    action: Literal["choose_intrigue_target"] = "choose_intrigue_target"
    target_player_id: str


class QuestRewardChoiceRequest(BaseModel):
    action: Literal["quest_reward_choice"] = "quest_reward_choice"
    choice_id: str


class ResourceChoiceRequest(BaseModel):
    action: Literal["resource_choice"] = "resource_choice"
    prompt_id: str
    chosen_resources: dict = Field(default_factory=dict)


class ReconnectRequest(BaseModel):
    action: Literal["reconnect"] = "reconnect"
    game_code: str
    player_name: str
    slot_index: int = Field(ge=0)


class PingRequest(BaseModel):
    action: Literal["ping"] = "ping"


ClientMessage = Annotated[
    Union[
        CreateGameRequest,
        JoinGameRequest,
        PlayerReadyRequest,
        StartGameRequest,
        PlaceWorkerRequest,
        PlaceWorkerBackstageRequest,
        SelectQuestCardRequest,
        CompleteQuestRequest,
        AcquireContractRequest,
        AcquireIntrigueRequest,
        PurchaseBuildingRequest,
        CancelPurchaseBuildingRequest,
        CancelQuestSelectionRequest,
        SkipQuestCompletionRequest,
        ReassignWorkerRequest,
        ChooseIntrigueTargetRequest,
        QuestRewardChoiceRequest,
        CancelIntrigueTargetRequest,
        ResourceChoiceRequest,
        ReconnectRequest,
        PingRequest,
    ],
    Field(discriminator="action"),
]

client_message_adapter: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)


def parse_client_message(raw: str | bytes) -> ClientMessage:
    """Parse a raw JSON string into the appropriate client message type."""
    return client_message_adapter.validate_json(raw)


# ---------------------------------------------------------------------------
# Server -> Client messages
# ---------------------------------------------------------------------------


class LobbyPlayerInfo(BaseModel):
    player_id: str
    name: str
    slot_index: int
    ready: bool = False


class GameCreatedResponse(BaseModel):
    action: Literal["game_created"] = "game_created"
    game_code: str
    player_id: str
    slot_index: int


class PlayerJoinedResponse(BaseModel):
    action: Literal["player_joined"] = "player_joined"
    player_name: str
    slot_index: int
    players: list[LobbyPlayerInfo]


class PlayerReadyUpdateResponse(BaseModel):
    action: Literal["player_ready_update"] = "player_ready_update"
    player_id: str
    ready: bool


class GameStartedResponse(BaseModel):
    action: Literal["game_started"] = "game_started"
    game_state: dict  # Filtered game state per player


class WorkerPlacedResponse(BaseModel):
    action: Literal["worker_placed"] = "worker_placed"
    player_id: str
    space_id: str
    reward_granted: dict
    owner_bonus: dict = Field(default_factory=dict)
    next_player_id: str | None


class WorkerPlacedBackstageResponse(BaseModel):
    action: Literal["worker_placed_backstage"] = "worker_placed_backstage"
    player_id: str
    slot_number: int
    intrigue_card: dict
    intrigue_effect: dict
    next_player_id: str | None


class QuestCardSelectedResponse(BaseModel):
    action: Literal["quest_card_selected"] = "quest_card_selected"
    player_id: str
    card_id: str
    spot_number: int
    bonus_reward: dict
    next_player_id: str | None


class FaceUpQuestsUpdatedResponse(BaseModel):
    action: Literal["face_up_quests_updated"] = "face_up_quests_updated"
    face_up_quests: list[dict]


class QuestsResetResponse(BaseModel):
    action: Literal["quests_reset"] = "quests_reset"
    player_id: str
    deck_reshuffled: bool = False
    next_player_id: str | None


class QuestCompletedResponse(BaseModel):
    action: Literal["quest_completed"] = "quest_completed"
    player_id: str
    contract_id: str
    contract_name: str
    victory_points_earned: int
    resources_spent: dict
    bonus_resources: dict
    drawn_intrigue: list[dict] = Field(
        default_factory=list,
    )
    drawn_quests: list[dict] = Field(
        default_factory=list,
    )
    building_granted: dict | None = None
    pending_choice: bool = False
    next_player_id: str | None = None


class QuestCompletionPromptResponse(BaseModel):
    action: Literal["quest_completion_prompt"] = "quest_completion_prompt"
    completable_quests: list[dict]


class QuestSkippedResponse(BaseModel):
    action: Literal["quest_skipped"] = "quest_skipped"
    player_id: str
    next_player_id: str | None = None


class ContractAcquiredResponse(BaseModel):
    action: Literal["contract_acquired"] = "contract_acquired"
    player_id: str
    contract_id: str
    new_face_up: dict | None = None


class PlacementCancelledResponse(BaseModel):
    action: Literal["placement_cancelled"] = "placement_cancelled"
    player_id: str
    space_id: str
    next_player_id: str | None
    returned_card: dict = Field(default_factory=dict)


class BuildingConstructedResponse(BaseModel):
    action: Literal["building_constructed"] = "building_constructed"
    player_id: str
    building_id: str
    building_name: str
    lot_index: int
    new_space_id: str
    visitor_reward: dict = Field(default_factory=dict)
    owner_bonus: dict = Field(default_factory=dict)
    owner_id: str = ""
    cost_coins: int = 0
    accumulated_vp: int = 0
    next_player_id: str | None = None


class BuildingMarketUpdateResponse(BaseModel):
    action: Literal["building_market_update"] = "building_market_update"
    face_up_buildings: list[dict]
    deck_remaining: int


class ReassignmentPhaseStartResponse(BaseModel):
    action: Literal["reassignment_phase_start"] = "reassignment_phase_start"
    backstage_slots: list[dict]


class WorkerReassignedResponse(BaseModel):
    action: Literal["worker_reassigned"] = "worker_reassigned"
    player_id: str
    from_slot: int
    to_space_id: str
    reward_granted: dict
    owner_bonus: dict = Field(default_factory=dict)


class RoundEndResponse(BaseModel):
    action: Literal["round_end"] = "round_end"
    round_number: int
    next_round: int
    first_player_id: str | None
    turn_order: list[str] = Field(default_factory=list)
    bonus_worker_granted: bool = False


class BonusWorkersGrantedResponse(BaseModel):
    action: Literal["bonus_workers_granted"] = "bonus_workers_granted"
    round: int
    new_worker_count: int


class FinalPlayerScore(BaseModel):
    player_id: str
    player_name: str
    base_vp: int
    producer_bonus: int
    producer_card: dict
    total_vp: int
    rank: int


class GameOverResponse(BaseModel):
    action: Literal["game_over"] = "game_over"
    final_scores: list[FinalPlayerScore]
    tiebreaker_applied: bool = False


class StateSyncResponse(BaseModel):
    action: Literal["state_sync"] = "state_sync"
    game_state: dict


class ErrorResponse(BaseModel):
    action: Literal["error"] = "error"
    code: str
    message: str


class PongResponse(BaseModel):
    action: Literal["pong"] = "pong"


class PlayerDisconnectedResponse(BaseModel):
    action: Literal["player_disconnected"] = "player_disconnected"
    player_id: str
    player_name: str


class PlayerReconnectedResponse(BaseModel):
    action: Literal["player_reconnected"] = "player_reconnected"
    player_id: str
    player_name: str


class QuestRewardChoicePromptResponse(BaseModel):
    action: Literal["quest_reward_choice_prompt"] = "quest_reward_choice_prompt"
    reward_type: str
    available_choices: list[dict]
    quest_name: str


class QuestRewardChoiceResolvedResponse(BaseModel):
    action: Literal["quest_reward_choice_resolved"] = "quest_reward_choice_resolved"
    player_id: str
    reward_type: str
    choice: dict
    quest_name: str
    next_player_id: str | None = None


class IntrigueTargetPromptResponse(BaseModel):
    action: Literal["intrigue_target_prompt"] = "intrigue_target_prompt"
    effect_type: str
    effect_value: dict
    eligible_targets: list[dict]


class IntrigueEffectResolvedResponse(BaseModel):
    action: Literal["intrigue_effect_resolved"] = "intrigue_effect_resolved"
    player_id: str
    target_player_id: str
    effect_type: str
    resources_affected: dict


class ResourceChoicePromptResponse(BaseModel):
    action: Literal["resource_choice_prompt"] = "resource_choice_prompt"
    prompt_id: str
    player_id: str
    choice_type: str
    title: str
    description: str
    allowed_types: list[str] = Field(default_factory=list)
    pick_count: int = 0
    total: int = 0
    bundles: list[dict] = Field(default_factory=list)
    is_spend: bool = False


class ResourceChoiceResolvedResponse(BaseModel):
    action: Literal["resource_choice_resolved"] = "resource_choice_resolved"
    player_id: str
    chosen_resources: dict
    is_spend: bool = False
    source_description: str = ""
    next_player_id: str | None = None


class TurnTimeoutResponse(BaseModel):
    action: Literal["turn_timeout"] = "turn_timeout"
    player_id: str
    player_name: str
    skipped: bool = True


ServerMessage = Annotated[
    Union[
        GameCreatedResponse,
        PlayerJoinedResponse,
        PlayerReadyUpdateResponse,
        GameStartedResponse,
        WorkerPlacedResponse,
        WorkerPlacedBackstageResponse,
        QuestCardSelectedResponse,
        FaceUpQuestsUpdatedResponse,
        QuestsResetResponse,
        QuestCompletedResponse,
        QuestCompletionPromptResponse,
        QuestSkippedResponse,
        ContractAcquiredResponse,
        PlacementCancelledResponse,
        BuildingConstructedResponse,
        BuildingMarketUpdateResponse,
        ReassignmentPhaseStartResponse,
        WorkerReassignedResponse,
        RoundEndResponse,
        BonusWorkersGrantedResponse,
        GameOverResponse,
        StateSyncResponse,
        ErrorResponse,
        PongResponse,
        PlayerDisconnectedResponse,
        PlayerReconnectedResponse,
        QuestRewardChoicePromptResponse,
        QuestRewardChoiceResolvedResponse,
        TurnTimeoutResponse,
        IntrigueTargetPromptResponse,
        IntrigueEffectResolvedResponse,
        ResourceChoicePromptResponse,
        ResourceChoiceResolvedResponse,
    ],
    Field(discriminator="action"),
]

server_message_adapter: TypeAdapter[ServerMessage] = TypeAdapter(ServerMessage)
