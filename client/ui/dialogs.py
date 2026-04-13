"""Modal dialogs for card selection, building purchase, etc."""

from __future__ import annotations

import arcade
import arcade.gui


class CardSelectionDialog:
    """A modal dialog for selecting a card from a list."""

    def __init__(
        self,
        title: str,
        cards: list[dict],
        on_select: callable,
        ui_manager: arcade.gui.UIManager,
    ) -> None:
        self.title = title
        self.cards = cards
        self.on_select = on_select
        self.ui = ui_manager
        self._widget = None

    def show(self, window_width: float, window_height: float) -> None:
        v_box = arcade.gui.UIBoxLayout(space_between=8)

        label = arcade.gui.UILabel(
            text=self.title,
            font_size=16,
            text_color=arcade.color.WHITE,
        )
        v_box.add(label)

        for card in self.cards[:8]:  # Show max 8 options
            name = card.get("name", "???")
            card_id = card.get("id", "")
            btn = arcade.gui.UIFlatButton(text=name, width=280, height=35)
            btn.on_click = lambda event, cid=card_id: self._select(cid)
            v_box.add(btn)

        cancel_btn = arcade.gui.UIFlatButton(text="Cancel", width=280, height=35)
        cancel_btn.on_click = lambda event: self.hide()
        v_box.add(cancel_btn)

        self._widget = self.ui.add(arcade.gui.UIAnchorLayout())
        self._widget.add(child=v_box, anchor_x="center", anchor_y="center")

    def _select(self, card_id: str) -> None:
        self.hide()
        self.on_select(card_id)

    def hide(self) -> None:
        if self._widget:
            self.ui.remove(self._widget)
            self._widget = None


class ConfirmDialog:
    """A simple yes/no confirmation dialog."""

    def __init__(
        self,
        message: str,
        on_confirm: callable,
        ui_manager: arcade.gui.UIManager,
    ) -> None:
        self.message = message
        self.on_confirm = on_confirm
        self.ui = ui_manager
        self._widget = None

    def show(self) -> None:
        v_box = arcade.gui.UIBoxLayout(space_between=10)

        label = arcade.gui.UILabel(
            text=self.message,
            font_size=14,
            text_color=arcade.color.WHITE,
            multiline=True,
            width=300,
        )
        v_box.add(label)

        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        yes_btn = arcade.gui.UIFlatButton(text="Yes", width=120, height=40)
        yes_btn.on_click = lambda event: self._confirm(True)
        h_box.add(yes_btn)

        no_btn = arcade.gui.UIFlatButton(text="No", width=120, height=40)
        no_btn.on_click = lambda event: self._confirm(False)
        h_box.add(no_btn)

        v_box.add(h_box)

        self._widget = self.ui.add(arcade.gui.UIAnchorLayout())
        self._widget.add(child=v_box, anchor_x="center", anchor_y="center")

    def _confirm(self, result: bool) -> None:
        self.hide()
        if result:
            self.on_confirm()

    def hide(self) -> None:
        if self._widget:
            self.ui.remove(self._widget)
            self._widget = None
