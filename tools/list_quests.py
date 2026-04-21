"""Print a table of all quest cards with their victory points."""

import json
from pathlib import Path

config = Path(__file__).resolve().parent.parent / "config" / "contracts.json"
data = json.loads(config.read_text())


def resource_points(res: dict) -> float:
    return (
        res.get("singers", 0) * 1.0
        + res.get("drummers", 0) * 1.0
        + res.get("bass_players", 0) * 0.5
        + res.get("guitarists", 0) * 0.5
        + res.get("coins", 0) * 0.25
    )


def reward_points(c: dict) -> float:
    bonus = resource_points(c.get("bonus_resources", {}))
    bonus += c.get("reward_draw_intrigue", 0) * 1.0
    bonus += c.get("reward_draw_quests", 0) * 1.0
    return bonus


contracts = sorted(data["contracts"], key=lambda c: c["victory_points"])

print(
    f"{'Name':<45} {'Genre':<10}"
    f" {'Cost':>5} {'Reward':>6} {'VP':>3}"
    f" {'Value':>6} {'Benefit':>7}"
)
print("-" * 85)
for c in contracts:
    rc = resource_points(c["cost"])
    rw = reward_points(c)
    vp = c["victory_points"]
    value = rw + vp
    benefit = value - rc
    print(
        f"{c['name']:<45} {c['genre']:<10}"
        f" {rc:>5.2f} {rw:>6.2f} {vp:>3}"
        f" {value:>6.2f} {benefit:>7.2f}"
    )
print("-" * 85)
print(f"Total: {len(contracts)} quests")
