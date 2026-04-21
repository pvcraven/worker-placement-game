"""Tests for resource choice reward mechanics."""

from __future__ import annotations

import pytest

from shared.card_models import (
    ResourceBundle,
    ResourceChoiceReward,
    ResourceCost,
)
from server.game_engine import validate_resource_choice


@pytest.fixture
def pick_one_pending() -> dict:
    return {
        "choice_type": "pick",
        "allowed_types": [
            "guitarists",
            "bass_players",
            "drummers",
            "singers",
        ],
        "pick_count": 1,
    }


@pytest.fixture
def pick_two_pending() -> dict:
    return {
        "choice_type": "pick",
        "allowed_types": [
            "guitarists",
            "bass_players",
            "drummers",
            "singers",
        ],
        "pick_count": 2,
    }


@pytest.fixture
def bundle_pending() -> dict:
    return {
        "choice_type": "bundle",
        "bundles": [
            {
                "label": "1 Singer",
                "resources": {
                    "singers": 1,
                    "guitarists": 0,
                    "bass_players": 0,
                    "drummers": 0,
                    "coins": 0,
                },
            },
            {
                "label": "2 Guitarists",
                "resources": {
                    "guitarists": 2,
                    "singers": 0,
                    "bass_players": 0,
                    "drummers": 0,
                    "coins": 0,
                },
            },
            {
                "label": "4 Coins",
                "resources": {
                    "coins": 4,
                    "guitarists": 0,
                    "bass_players": 0,
                    "drummers": 0,
                    "singers": 0,
                },
            },
        ],
    }


@pytest.fixture
def combo_pending() -> dict:
    return {
        "choice_type": "combo",
        "allowed_types": ["guitarists", "bass_players"],
        "total": 4,
    }


class TestPickMode:
    def test_valid_single_pick(self, pick_one_pending):
        err = validate_resource_choice(
            pick_one_pending,
            {"guitarists": 1},
        )
        assert err is None

    def test_valid_pick_different_type(
        self,
        pick_one_pending,
    ):
        err = validate_resource_choice(
            pick_one_pending,
            {"singers": 1},
        )
        assert err is None

    def test_valid_multi_pick_same_type(
        self,
        pick_two_pending,
    ):
        err = validate_resource_choice(
            pick_two_pending,
            {"guitarists": 2},
        )
        assert err is None

    def test_valid_multi_pick_split(
        self,
        pick_two_pending,
    ):
        err = validate_resource_choice(
            pick_two_pending,
            {"guitarists": 1, "drummers": 1},
        )
        assert err is None

    def test_reject_wrong_count_too_many(
        self,
        pick_one_pending,
    ):
        err = validate_resource_choice(
            pick_one_pending,
            {"guitarists": 2},
        )
        assert err is not None
        assert "exactly 1" in err

    def test_reject_wrong_count_too_few(
        self,
        pick_two_pending,
    ):
        err = validate_resource_choice(
            pick_two_pending,
            {"guitarists": 1},
        )
        assert err is not None
        assert "exactly 2" in err

    def test_reject_disallowed_type(
        self,
        pick_one_pending,
    ):
        err = validate_resource_choice(
            pick_one_pending,
            {"coins": 1},
        )
        assert err is not None
        assert "not an allowed" in err

    def test_reject_zero_picks(self, pick_one_pending):
        err = validate_resource_choice(
            pick_one_pending,
            {},
        )
        assert err is not None

    def test_reject_negative_value(
        self,
        pick_one_pending,
    ):
        err = validate_resource_choice(
            pick_one_pending,
            {"guitarists": -1},
        )
        assert err is not None


class TestBundleMode:
    def test_valid_bundle_selection(
        self,
        bundle_pending,
    ):
        err = validate_resource_choice(
            bundle_pending,
            {
                "singers": 1,
                "guitarists": 0,
                "bass_players": 0,
                "drummers": 0,
                "coins": 0,
            },
        )
        assert err is None

    def test_valid_bundle_coins(self, bundle_pending):
        err = validate_resource_choice(
            bundle_pending,
            {
                "coins": 4,
                "guitarists": 0,
                "bass_players": 0,
                "drummers": 0,
                "singers": 0,
            },
        )
        assert err is None

    def test_reject_no_matching_bundle(
        self,
        bundle_pending,
    ):
        err = validate_resource_choice(
            bundle_pending,
            {"drummers": 3},
        )
        assert err is not None
        assert "does not match" in err

    def test_reject_partial_bundle(
        self,
        bundle_pending,
    ):
        err = validate_resource_choice(
            bundle_pending,
            {"singers": 2},
        )
        assert err is not None


class TestComboMode:
    def test_valid_combo_full_one_type(
        self,
        combo_pending,
    ):
        err = validate_resource_choice(
            combo_pending,
            {"guitarists": 4},
        )
        assert err is None

    def test_valid_combo_split(self, combo_pending):
        err = validate_resource_choice(
            combo_pending,
            {"guitarists": 3, "bass_players": 1},
        )
        assert err is None

    def test_valid_combo_even_split(
        self,
        combo_pending,
    ):
        err = validate_resource_choice(
            combo_pending,
            {"guitarists": 2, "bass_players": 2},
        )
        assert err is None

    def test_reject_combo_over_total(
        self,
        combo_pending,
    ):
        err = validate_resource_choice(
            combo_pending,
            {"guitarists": 5},
        )
        assert err is not None
        assert "exactly 4" in err

    def test_reject_combo_under_total(
        self,
        combo_pending,
    ):
        err = validate_resource_choice(
            combo_pending,
            {"guitarists": 2},
        )
        assert err is not None

    def test_reject_combo_disallowed_type(
        self,
        combo_pending,
    ):
        err = validate_resource_choice(
            combo_pending,
            {"guitarists": 2, "singers": 2},
        )
        assert err is not None
        assert "not an allowed" in err


class TestResourceChoiceRewardModel:
    def test_pick_model(self):
        r = ResourceChoiceReward(
            choice_type="pick",
            allowed_types=["guitarists", "singers"],
            pick_count=1,
        )
        assert r.choice_type == "pick"
        assert r.pick_count == 1

    def test_bundle_model(self):
        r = ResourceChoiceReward(
            choice_type="bundle",
            bundles=[
                ResourceBundle(
                    label="Test",
                    resources=ResourceCost(coins=4),
                ),
            ],
        )
        assert len(r.bundles) == 1
        assert r.bundles[0].resources.coins == 4

    def test_combo_model(self):
        r = ResourceChoiceReward(
            choice_type="combo",
            allowed_types=["guitarists", "bass_players"],
            total=4,
            cost=ResourceCost(coins=2),
        )
        assert r.total == 4
        assert r.cost.coins == 2

    def test_exchange_model(self):
        r = ResourceChoiceReward(
            choice_type="exchange",
            allowed_types=[
                "guitarists",
                "bass_players",
                "drummers",
                "singers",
            ],
            pick_count=2,
            gain_count=3,
        )
        assert r.pick_count == 2
        assert r.gain_count == 3
