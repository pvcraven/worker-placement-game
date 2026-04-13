"""End-of-game results view: final scores, producer reveals, winner."""

from __future__ import annotations

import arcade
import arcade.gui


class ResultsView(arcade.View):
    """Displays final scores and the winner."""

    def __init__(self) -> None:
        super().__init__()
        self.ui = arcade.gui.UIManager()
        self._setup_done = False

    def on_show_view(self) -> None:
        self.ui.enable()
        if not self._setup_done:
            self._build_ui()
            self._setup_done = True

    def on_hide_view(self) -> None:
        self.ui.disable()

    def _build_ui(self) -> None:
        self.ui.clear()

        scores = getattr(self.window, "final_scores", [])
        tiebreaker = getattr(self.window, "tiebreaker", False)

        v_box = arcade.gui.UIBoxLayout(space_between=10)

        title = arcade.gui.UILabel(
            text="Game Over!",
            font_size=32,
            text_color=arcade.color.WHITE,
            align="center",
        )
        v_box.add(title)

        if scores:
            winner = scores[0]
            winner_label = arcade.gui.UILabel(
                text=f"Winner: {winner.get('player_name', '???')}",
                font_size=24,
                text_color=arcade.color.GOLD,
                align="center",
            )
            v_box.add(winner_label)

        spacer = arcade.gui.UISpace(height=20)
        v_box.add(spacer)

        # Score table
        header = arcade.gui.UILabel(
            text=f"{'Rank':<6}{'Player':<20}{'Base VP':<10}{'Producer':<10}{'Total':<8}",
            font_size=13,
            text_color=arcade.color.LIGHT_GRAY,
        )
        v_box.add(header)

        for s in scores:
            rank = s.get("rank", "?")
            name = s.get("player_name", "???")[:18]
            base = s.get("base_vp", 0)
            bonus = s.get("producer_bonus", 0)
            total = s.get("total_vp", 0)
            line = f"#{rank:<5}{name:<20}{base:<10}{'+' + str(bonus):<10}{total:<8}"
            color = arcade.color.GOLD if rank == 1 else arcade.color.WHITE
            row = arcade.gui.UILabel(text=line, font_size=13, text_color=color)
            v_box.add(row)

        # Producer card reveals
        spacer2 = arcade.gui.UISpace(height=15)
        v_box.add(spacer2)

        reveal_label = arcade.gui.UILabel(
            text="Producer Card Reveals:",
            font_size=14,
            text_color=arcade.color.LIGHT_GRAY,
        )
        v_box.add(reveal_label)

        for s in scores:
            pcard = s.get("producer_card", {})
            pname = pcard.get("name", "Unknown")
            player_name = s.get("player_name", "???")
            reveal = arcade.gui.UILabel(
                text=f"  {player_name}: {pname}",
                font_size=12,
                text_color=arcade.color.WHITE,
            )
            v_box.add(reveal)

        if tiebreaker:
            tb_label = arcade.gui.UILabel(
                text="(Tiebreaker applied)",
                font_size=12,
                text_color=arcade.color.YELLOW,
            )
            v_box.add(tb_label)

        spacer3 = arcade.gui.UISpace(height=20)
        v_box.add(spacer3)

        # Return to menu button
        menu_btn = arcade.gui.UIFlatButton(text="Return to Menu", width=250, height=45)
        menu_btn.on_click = self._on_menu
        v_box.add(menu_btn)

        anchor = self.ui.add(arcade.gui.UIAnchorLayout())
        anchor.add(child=v_box, anchor_x="center", anchor_y="center")

    def _on_menu(self, event) -> None:
        self.window.network.disconnect()
        self.window.show_menu()

    def on_draw(self) -> None:
        self.clear()
        self.ui.draw()
