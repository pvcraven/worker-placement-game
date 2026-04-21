"""Print a formatted table of all buildings from buildings.json."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "config" / "buildings.json"

SYM = {
    "guitarists": "G",
    "bass_players": "B",
    "drummers": "D",
    "singers": "S",
    "coins": "$",
}


def _res_str(res: dict) -> str:
    parts = [f"{v}{SYM[k]}" for k, v in res.items() if v]
    return " ".join(parts) if parts else "-"


def _choice_str(choice: dict) -> str:
    ct = choice["choice_type"]
    types = "/".join(SYM.get(t, t) for t in choice.get("allowed_types", []))
    if ct == "pick":
        return f"Pick {choice['pick_count']} {types}"
    if ct == "combo":
        cost = choice.get("cost", {})
        cost_parts = [f"{v}{SYM[k]}" for k, v in cost.items() if v]
        cost_str = f"Pay {' '.join(cost_parts)}, " if cost_parts else ""
        return f"{cost_str}Combo {choice['total']} {types}"
    if ct == "exchange":
        return f"Trade {choice['pick_count']}->{choice['gain_count']} {types}"
    if ct == "bundle":
        labels = [b["label"] for b in choice.get("bundles", [])]
        return "Choose: " + " / ".join(labels[:3])
    return ct


def main() -> None:
    data = json.loads(CONFIG.read_text())
    buildings = data["buildings"]

    headers = ["#", "Name", "Cost", "Visitor Reward", "Special", "Owner Bonus", "Owner Special"]
    rows = []
    for i, b in enumerate(buildings, 1):
        visitor = _res_str(b["visitor_reward"])
        choice = b.get("visitor_reward_choice")
        if choice:
            visitor += " + " + _choice_str(choice)
        special = b.get("visitor_reward_special") or ""
        if special:
            special = special.replace("_", " ")
        owner = _res_str(b["owner_bonus"])
        owner_special = b.get("owner_bonus_special") or ""
        if owner_special:
            owner_special = owner_special.replace("_", " ")
        rows.append([
            str(i),
            b["name"],
            str(b["cost_coins"]),
            visitor,
            special,
            owner,
            owner_special,
        ])

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(cells: list[str]) -> str:
        padded = [c.ljust(col_widths[i]) for i, c in enumerate(cells)]
        return "| " + " | ".join(padded) + " |"

    sep = "|-" + "-|-".join("-" * w for w in col_widths) + "-|"

    print(fmt_row(headers))
    print(sep)
    for row in rows:
        print(fmt_row(row))


if __name__ == "__main__":
    main()
