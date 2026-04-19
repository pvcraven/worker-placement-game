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
        on_cancel: callable | None = None,
    ) -> None:
        self.title = title
        self.cards = cards
        self.on_select = on_select
        self.on_cancel = on_cancel
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
        cancel_btn.on_click = lambda event: self._cancel()
        v_box.add(cancel_btn)

        bg_box = v_box.with_padding(all=20).with_background(
            color=(0, 0, 0)
        )
        self._widget = self.ui.add(arcade.gui.UIAnchorLayout())
        self._widget.add(child=bg_box, anchor_x="center", anchor_y="center")

    def _select(self, card_id: str) -> None:
        self.hide()
        self.on_select(card_id)

    def _cancel(self) -> None:
        self.hide()
        if self.on_cancel:
            self.on_cancel()

    def hide(self) -> None:
        if self._widget:
            self.ui.remove(self._widget)
            self._widget = None


class BuildingPurchaseDialog:
    """A modal dialog for purchasing a building from the face-up market."""

    def __init__(
        self,
        buildings: list[dict],
        player_coins: int,
        on_purchase: callable,
        on_cancel: callable,
        ui_manager: arcade.gui.UIManager,
    ) -> None:
        self.buildings = buildings
        self.player_coins = player_coins
        self.on_purchase = on_purchase
        self.on_cancel = on_cancel
        self.ui = ui_manager
        self._widget = None

    def show(self, window_width: float, window_height: float) -> None:
        v_box = arcade.gui.UIBoxLayout(space_between=8)

        label = arcade.gui.UILabel(
            text="Real Estate Listings",
            font_size=16,
            text_color=arcade.color.WHITE,
        )
        v_box.add(label)

        coins_label = arcade.gui.UILabel(
            text=f"Your coins: {self.player_coins}",
            font_size=13,
            text_color=arcade.color.GOLD,
        )
        v_box.add(coins_label)

        if not self.buildings:
            empty_label = arcade.gui.UILabel(
                text="No buildings available for purchase.",
                font_size=13,
                text_color=arcade.color.LIGHT_GRAY,
            )
            v_box.add(empty_label)
        else:
            for building in self.buildings:
                bid = building.get("id", "")
                name = building.get("name", "???")
                cost = building.get("cost_coins", 0)
                vp = building.get("accumulated_vp", 0)
                can_afford = self.player_coins >= cost

                # Build reward summary
                reward = building.get("visitor_reward", {})
                reward_parts = []
                for key, sym in [("guitarists", "G"), ("bass_players", "B"),
                                 ("drummers", "D"), ("singers", "S"), ("coins", "$")]:
                    val = reward.get(key, 0)
                    if val > 0:
                        reward_parts.append(f"{val}{sym}")
                reward_str = " ".join(reward_parts) if reward_parts else "Special"

                btn_text = f"{name} | {cost}$ | {vp}VP | {reward_str}"
                if not can_afford:
                    btn_text = f"[Can't afford] {btn_text}"

                btn = arcade.gui.UIFlatButton(
                    text=btn_text, width=400, height=35,
                )
                if can_afford:
                    btn.on_click = lambda event, b=bid: self._purchase(b)
                else:
                    btn.on_click = lambda event: None  # Disabled
                v_box.add(btn)

        cancel_btn = arcade.gui.UIFlatButton(
            text="Cancel", width=400, height=35,
        )
        cancel_btn.on_click = lambda event: self._cancel()
        v_box.add(cancel_btn)

        bg_box = v_box.with_padding(all=20).with_background(
            color=(0, 0, 0)
        )
        self._widget = self.ui.add(arcade.gui.UIAnchorLayout())
        self._widget.add(child=bg_box, anchor_x="center", anchor_y="center")

    def _purchase(self, building_id: str) -> None:
        self.hide()
        self.on_purchase(building_id)

    def _cancel(self) -> None:
        self.hide()
        self.on_cancel()

    def hide(self) -> None:
        if self._widget:
            self.ui.remove(self._widget)
            self._widget = None


class QuestCompletionDialog:
    """A modal dialog for completing a quest at end of turn.

    Renders quest cards as sprites and handles
    click detection on them directly.
    """

    _CARD_WIDTH = 190
    _CARD_HEIGHT = 230

    def __init__(
        self,
        quests: list[dict],
        on_select: callable,
        on_skip: callable,
    ) -> None:
        self.quests = quests[:6]
        self.on_select = on_select
        self.on_skip = on_skip
        self._card_rects: list[
            tuple[str, float, float, float, float]
        ] = []
        self._skip_rect = (0.0, 0.0, 0.0, 0.0)
        self._visible = False
        self._quest_sprite_list: arcade.SpriteList | None = None

    def show(
        self, window_width: float, window_height: float,
    ) -> None:
        self._visible = True
        self._ww = window_width
        self._wh = window_height
        self._layout()

    def _layout(self) -> None:
        cw = self._CARD_WIDTH
        ch = self._CARD_HEIGHT
        self._card_rects.clear()
        n = len(self.quests)
        spacing = cw + 15
        total_w = n * spacing
        panel_h = ch + 120
        pcx = self._ww / 2
        pcy = self._wh / 2
        card_cy = pcy + 20
        start_x = pcx - total_w / 2 + cw / 2
        for i, quest in enumerate(self.quests):
            cx = start_x + i * spacing
            qid = quest.get("id", "")
            left = cx - cw / 2
            bottom = card_cy - ch / 2
            self._card_rects.append((
                qid, left, bottom, cw, ch,
            ))
        skip_w, skip_h = 200, 35
        self._skip_rect = (
            pcx - skip_w / 2,
            pcy - panel_h / 2 + 15,
            skip_w,
            skip_h,
        )

    def draw(self, ww: float, wh: float) -> None:
        if not self._visible:
            return
        from client.ui.board_renderer import (
            _build_card_sprite_list,
        )
        cw = self._CARD_WIDTH
        ch = self._CARD_HEIGHT
        n = len(self.quests)
        spacing = cw + 15
        total_w = n * spacing
        panel_w = total_w + 40
        panel_h = ch + 120
        pcx = ww / 2
        pcy = wh / 2
        arcade.draw_rect_filled(
            arcade.rect.XYWH(pcx, pcy, panel_w, panel_h),
            (0, 0, 0),
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(pcx, pcy, panel_w, panel_h),
            arcade.color.WHITE,
            border_width=1,
        )
        arcade.Text(
            "Complete a Quest?",
            pcx, pcy + panel_h / 2 - 22,
            arcade.color.WHITE,
            font_size=16,
            font_name="Tahoma",
            anchor_x="center",
            anchor_y="center",
        ).draw()

        start_x = pcx - total_w / 2 + cw / 2
        cy = pcy + 20
        positions = [
            (start_x + i * spacing, cy)
            for i in range(n)
        ]
        self._quest_sprite_list = _build_card_sprite_list(
            self.quests, "quests", positions,
        )
        self._quest_sprite_list.draw()

        # Skip button
        sl, sb, sw, sh = self._skip_rect
        scx = sl + sw / 2
        scy = sb + sh / 2
        arcade.draw_rect_filled(
            arcade.rect.XYWH(scx, scy, sw, sh),
            (60, 60, 60),
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(scx, scy, sw, sh),
            arcade.color.WHITE,
            border_width=1,
        )
        arcade.Text(
            "Skip", scx, scy,
            arcade.color.WHITE,
            font_size=14,
            font_name="Tahoma",
            anchor_x="center",
            anchor_y="center",
        ).draw()

    def handle_click(
        self, x: float, y: float,
    ) -> bool:
        if not self._visible:
            return False
        for qid, left, bottom, cw, ch in self._card_rects:
            if (
                left <= x <= left + cw
                and bottom <= y <= bottom + ch
            ):
                self._select(qid)
                return True
        sl, sb, sw, sh = self._skip_rect
        if (
            sl <= x <= sl + sw
            and sb <= y <= sb + sh
        ):
            self._do_skip()
            return True
        return False

    def _select(self, contract_id: str) -> None:
        self.hide()
        self.on_select(contract_id)

    def _do_skip(self) -> None:
        self.hide()
        self.on_skip()

    def hide(self) -> None:
        self._visible = False
        self._card_rects.clear()


class RewardChoiceDialog:
    """A modal dialog for choosing a reward (quest or building)."""

    def __init__(
        self,
        title: str,
        description: str,
        choices: list[dict],
        label_key: str,
        on_select: callable,
        ui_manager: arcade.gui.UIManager,
    ) -> None:
        self.title = title
        self.description = description
        self.choices = choices
        self.label_key = label_key
        self.on_select = on_select
        self.ui = ui_manager
        self._widget = None

    def show(
        self, window_width: float, window_height: float,
    ) -> None:
        v_box = arcade.gui.UIBoxLayout(space_between=8)

        label = arcade.gui.UILabel(
            text=self.title,
            font_size=16,
            text_color=arcade.color.WHITE,
        )
        v_box.add(label)

        desc = arcade.gui.UILabel(
            text=self.description,
            font_size=13,
            text_color=arcade.color.LIGHT_GRAY,
        )
        v_box.add(desc)

        for item in self.choices[:8]:
            name = item.get(self.label_key, "???")
            item_id = item.get("id", "")
            btn = arcade.gui.UIFlatButton(
                text=name, width=320, height=35,
            )
            btn.on_click = (
                lambda event, cid=item_id: self._select(cid)
            )
            v_box.add(btn)

        bg_box = v_box.with_padding(
            all=20,
        ).with_background(color=(0, 0, 0))
        self._widget = self.ui.add(
            arcade.gui.UIAnchorLayout(),
        )
        self._widget.add(
            child=bg_box,
            anchor_x="center",
            anchor_y="center",
        )

    def _select(self, choice_id: str) -> None:
        self.hide()
        self.on_select(choice_id)

    def hide(self) -> None:
        if self._widget:
            self.ui.remove(self._widget)
            self._widget = None


class PlayerTargetDialog:
    """A modal dialog for selecting a target opponent."""

    def __init__(
        self,
        title: str,
        effect_description: str,
        eligible_targets: list[dict],
        on_select: callable,
        on_cancel: callable,
        ui_manager: arcade.gui.UIManager,
    ) -> None:
        self.title = title
        self.effect_description = effect_description
        self.eligible_targets = eligible_targets
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.ui = ui_manager
        self._widget = None

    def show(
        self, window_width: float, window_height: float,
    ) -> None:
        v_box = arcade.gui.UIBoxLayout(space_between=8)

        label = arcade.gui.UILabel(
            text=self.title,
            font_size=16,
            text_color=arcade.color.WHITE,
        )
        v_box.add(label)

        desc_label = arcade.gui.UILabel(
            text=self.effect_description,
            font_size=12,
            text_color=arcade.color.GOLD,
        )
        v_box.add(desc_label)

        for target in self.eligible_targets:
            pid = target.get("player_id", "")
            name = target.get("player_name", "???")
            res = target.get("resources", {})
            res_parts = []
            mapping = [
                ("guitarists", "G"),
                ("bass_players", "B"),
                ("drummers", "D"),
                ("singers", "S"),
                ("coins", "$"),
            ]
            for key, sym in mapping:
                val = res.get(key, 0)
                if val > 0:
                    res_parts.append(f"{val}{sym}")
            res_str = (
                " ".join(res_parts)
                if res_parts
                else "no resources"
            )
            btn_text = f"{name} ({res_str})"
            btn = arcade.gui.UIFlatButton(
                text=btn_text, width=350, height=35,
            )
            btn.on_click = (
                lambda event, p=pid: self._select(p)
            )
            v_box.add(btn)

        cancel_btn = arcade.gui.UIFlatButton(
            text="Cancel", width=350, height=35,
        )
        cancel_btn.on_click = lambda event: self._cancel()
        v_box.add(cancel_btn)

        bg_box = v_box.with_padding(
            all=20,
        ).with_background(color=(0, 0, 0))
        self._widget = self.ui.add(
            arcade.gui.UIAnchorLayout(),
        )
        self._widget.add(
            child=bg_box,
            anchor_x="center",
            anchor_y="center",
        )

    def _select(self, player_id: str) -> None:
        self.hide()
        self.on_select(player_id)

    def _cancel(self) -> None:
        self.hide()
        self.on_cancel()

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
