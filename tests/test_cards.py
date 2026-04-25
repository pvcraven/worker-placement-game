"""Unit tests for quest card (contract) data integrity."""

import json
from collections import Counter
from pathlib import Path

import pytest

CONFIG = Path(__file__).resolve().parent.parent / "config" / "contracts.json"


@pytest.fixture(scope="module")
def contracts():
    data = json.loads(CONFIG.read_text())
    return data["contracts"]


@pytest.fixture(scope="module")
def genre_counts(contracts):
    return Counter(c["genre"] for c in contracts)


def test_equal_cards_per_genre(genre_counts):
    counts = list(genre_counts.values())
    assert len(counts) > 0, "No genres found"
    assert all(
        c == counts[0] for c in counts
    ), f"Unequal cards per genre: {dict(genre_counts)}"


def _resource_points(res: dict) -> float:
    return (
        res.get("singers", 0) * 1.0
        + res.get("drummers", 0) * 1.0
        + res.get("bass_players", 0) * 0.5
        + res.get("guitarists", 0) * 0.5
        + res.get("coins", 0) * 0.25
    )


def _benefit(card: dict) -> float:
    return _reward(card) + card["victory_points"] - _cost(card)


def _cost(card: dict) -> float:
    return _resource_points(card["cost"])


def _reward(card: dict) -> float:
    rw = _resource_points(card.get("bonus_resources", {}))
    rw += card.get("reward_draw_intrigue", 0) * 1.0
    rw += card.get("reward_draw_quests", 0) * 1.0
    return rw


def test_all_cards_have_minimum_benefit(contracts):
    min_benefit = 1.0
    non_plot = [c for c in contracts if not c.get("is_plot_quest")]
    bad = [(c["name"], _benefit(c)) for c in non_plot if _benefit(c) < min_benefit]
    assert not bad, f"Cards with benefit < {min_benefit}: " + ", ".join(
        f"{name} ({b:.2f})" for name, b in bad
    )


def test_benefit_not_more_than_four_and_half_times_cost(contracts):
    bad = []
    non_plot = [c for c in contracts if not c.get("is_plot_quest")]
    for c in non_plot:
        cost = _cost(c)
        benefit = _benefit(c)
        if benefit > cost * 4.5:
            bad.append(
                (c["name"], cost, benefit, f"{benefit / cost:.1f}x" if cost else "inf")
            )
    assert not bad, "Cards with benefit > 4.5x cost: " + ", ".join(
        f"{name} (cost={c:.2f}, benefit={b:.2f}, " f"ratio={r})"
        for name, c, b, r in bad
    )


def test_genre_total_benefit_balanced(contracts):
    from collections import defaultdict

    totals = defaultdict(float)
    for c in contracts:
        totals[c["genre"]] += _benefit(c)

    genres = sorted(totals.keys())
    min_total = min(totals.values())
    max_total = max(totals.values())
    spread = max_total - min_total

    summary = ", ".join(f"{g}={totals[g]:.2f}" for g in genres)
    assert spread <= 10.0, f"Genre benefit spread {spread:.2f} > 10.0: " f"{summary}"


def _genre_resource_totals(contracts):
    from collections import defaultdict

    totals = defaultdict(lambda: defaultdict(int))
    for c in contracts:
        genre = c["genre"]
        cost = c["cost"]
        for resource in (
            "singers",
            "drummers",
            "guitarists",
            "bass_players",
            "coins",
        ):
            totals[genre][resource] += cost.get(resource, 0)
    return totals


def _assert_genre_leads_resource(
    totals,
    genre,
    resource,
    margin=0.10,
):
    genre_val = totals[genre][resource]
    others = {g: totals[g][resource] for g in totals if g != genre}
    for other_genre, other_val in others.items():
        threshold = other_val * (1 + margin)
        assert genre_val >= threshold, (
            f"{genre} {resource}={genre_val} is not 10%+ "
            f"more than {other_genre} "
            f"{resource}={other_val} "
            f"(needs >= {threshold:.1f}). "
            f"All: {dict({g: totals[g][resource] for g in sorted(totals)})}"
        )


def test_soul_requires_most_singers(contracts):
    totals = _genre_resource_totals(contracts)
    _assert_genre_leads_resource(totals, "soul", "singers")


def test_funk_requires_most_drummers(contracts):
    totals = _genre_resource_totals(contracts)
    _assert_genre_leads_resource(totals, "funk", "drummers")


def test_rock_requires_most_guitarists(contracts):
    totals = _genre_resource_totals(contracts)
    _assert_genre_leads_resource(
        totals,
        "rock",
        "guitarists",
    )


def test_pop_requires_most_coins(contracts):
    totals = _genre_resource_totals(contracts)
    _assert_genre_leads_resource(totals, "pop", "coins")


def test_jazz_requires_most_bass_players(contracts):
    totals = _genre_resource_totals(contracts)
    _assert_genre_leads_resource(
        totals,
        "jazz",
        "bass_players",
    )
