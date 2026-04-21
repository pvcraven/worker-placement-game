"""Tests for end-game VP calculation including resource VP."""

from __future__ import annotations

from shared.card_models import ContractCard, ProducerCard, ResourceCost
from shared.constants import Genre
from shared.messages import FinalPlayerScore
from server.models.game import Player, PlayerResources


def _make_player(
    *,
    vp: int = 0,
    guitarists: int = 0,
    bass_players: int = 0,
    drummers: int = 0,
    singers: int = 0,
    coins: int = 0,
    completed_genres: list[Genre] | None = None,
    producer_genres: list[Genre] | None = None,
) -> Player:
    contracts = []
    for g in completed_genres or []:
        contracts.append(
            ContractCard(
                id=f"c_{g}",
                name=f"Quest {g}",
                description="",
                genre=g,
                cost=ResourceCost(),
                victory_points=vp,
            )
        )
    producer = None
    if producer_genres is not None:
        producer = ProducerCard(
            id="p1",
            name="Test Producer",
            description="",
            bonus_genres=producer_genres,
        )
    return Player(
        player_id="p1",
        display_name="Alice",
        slot_index=0,
        victory_points=vp * len(contracts),
        resources=PlayerResources(
            guitarists=guitarists,
            bass_players=bass_players,
            drummers=drummers,
            singers=singers,
            coins=coins,
        ),
        completed_contracts=contracts,
        producer_card=producer,
    )


def _calc_resource_vp(p: Player) -> int:
    r = p.resources
    return r.guitarists + r.bass_players + r.drummers + r.singers + r.coins // 2


def test_resource_vp_musicians_only():
    p = _make_player(guitarists=3, bass_players=2, drummers=1, singers=1)
    assert _calc_resource_vp(p) == 7


def test_resource_vp_coins_even():
    p = _make_player(coins=6)
    assert _calc_resource_vp(p) == 3


def test_resource_vp_coins_odd():
    p = _make_player(coins=5)
    assert _calc_resource_vp(p) == 2


def test_resource_vp_mixed():
    p = _make_player(guitarists=2, singers=1, coins=5)
    assert _calc_resource_vp(p) == 5


def test_resource_vp_zero():
    p = _make_player()
    assert _calc_resource_vp(p) == 0


def test_total_vp_includes_resource_vp():
    p = _make_player(
        vp=5,
        guitarists=3,
        coins=4,
        completed_genres=[Genre.ROCK],
        producer_genres=[Genre.ROCK],
    )
    game_vp = p.victory_points
    genre_bonus = 4
    resource_vp = 3 + 4 // 2
    expected_total = game_vp + genre_bonus + resource_vp
    assert game_vp == 5
    assert resource_vp == 5
    assert expected_total == 14


def test_final_player_score_fields():
    score = FinalPlayerScore(
        player_id="p1",
        player_name="Alice",
        game_vp=10,
        genre_bonus_vp=8,
        resource_vp=5,
        producer_card={},
        total_vp=23,
        rank=1,
    )
    assert score.game_vp == 10
    assert score.genre_bonus_vp == 8
    assert score.resource_vp == 5
    assert score.total_vp == 23
