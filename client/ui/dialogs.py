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


_RESOURCE_LABELS = {
    "guitarists": "Guitarist",
    "bass_players": "Bass Player",
    "drummers": "Drummer",
    "singers": "Singer",
    "coins": "Coin",
}


class ResourceChoiceDialog:
    """A modal dialog for choosing resources."""

    def __init__(
        self,
        prompt_id: str,
        title: str,
        description: str,
        choice_type: str,
        allowed_types: list[str],
        pick_count: int,
        total: int,
        bundles: list[dict],
        is_spend: bool,
        on_select: callable,
        ui_manager: arcade.gui.UIManager,
    ) -> None:
        self.prompt_id = prompt_id
        self.title = title
        self.description = description
        self.choice_type = choice_type
        self.allowed_types = allowed_types
        self.pick_count = pick_count
        self.total = total
        self.bundles = bundles
        self.is_spend = is_spend
        self.on_select = on_select
        self.ui = ui_manager
        self._widget = None
        self._selection: dict[str, int] = {}
        self._count_labels: dict[str, arcade.gui.UILabel] = {}
        self._total_label: arcade.gui.UILabel | None = None
        self._confirm_btn: arcade.gui.UIFlatButton | None = None

    def show(
        self, window_width: float, window_height: float,
    ) -> None:
        if self.choice_type == "bundle":
            self._show_bundle()
        elif self.choice_type == "combo":
            self._show_combo()
        else:
            self._show_pick()

    def _show_pick(self) -> None:
        v_box = arcade.gui.UIBoxLayout(space_between=8)
        self._add_header(v_box)

        target = self.pick_count
        self._selection = {t: 0 for t in self.allowed_types}
        info = arcade.gui.UILabel(
            text=f"Pick {target} resource(s):",
            font_size=13,
            text_color=arcade.color.LIGHT_GRAY,
        )
        v_box.add(info)

        for rtype in self.allowed_types:
            label = _RESOURCE_LABELS.get(rtype, rtype)
            btn = arcade.gui.UIFlatButton(
                text=label, width=320, height=35,
            )
            btn.on_click = (
                lambda e, rt=rtype: self._pick_add(rt)
            )
            v_box.add(btn)

        self._total_label = arcade.gui.UILabel(
            text="Selected: 0 / " + str(target),
            font_size=13,
            text_color=arcade.color.GOLD,
        )
        v_box.add(self._total_label)

        reset_btn = arcade.gui.UIFlatButton(
            text="Reset", width=320, height=30,
        )
        reset_btn.on_click = lambda e: self._pick_reset()
        v_box.add(reset_btn)

        self._mount(v_box)

    def _pick_add(self, rtype: str) -> None:
        target = self.pick_count
        current = sum(self._selection.values())
        if current >= target:
            return
        self._selection[rtype] = (
            self._selection.get(rtype, 0) + 1
        )
        current += 1
        if self._total_label:
            self._total_label.text = (
                f"Selected: {current} / {target}"
            )
        if current == target:
            self._do_select()

    def _pick_reset(self) -> None:
        self._selection = {
            t: 0 for t in self.allowed_types
        }
        if self._total_label:
            self._total_label.text = (
                f"Selected: 0 / {self.pick_count}"
            )

    def _show_bundle(self) -> None:
        v_box = arcade.gui.UIBoxLayout(space_between=8)
        self._add_header(v_box)

        for bundle in self.bundles:
            label = bundle.get("label", "???")
            res = bundle.get("resources", {})
            btn = arcade.gui.UIFlatButton(
                text=label, width=320, height=35,
            )
            btn.on_click = (
                lambda e, r=res: self._bundle_select(r)
            )
            v_box.add(btn)

        self._mount(v_box)

    def _bundle_select(self, resources: dict) -> None:
        self._selection = dict(resources)
        self._do_select()

    def _show_combo(self) -> None:
        v_box = arcade.gui.UIBoxLayout(space_between=8)
        self._add_header(v_box)
        self._selection = {t: 0 for t in self.allowed_types}

        for rtype in self.allowed_types:
            label = _RESOURCE_LABELS.get(rtype, rtype)
            row = arcade.gui.UIBoxLayout(
                vertical=False, space_between=8,
            )
            name_lbl = arcade.gui.UILabel(
                text=f"{label}:", font_size=13, width=120,
                text_color=arcade.color.WHITE,
            )
            row.add(name_lbl)

            minus_btn = arcade.gui.UIFlatButton(
                text="-", width=40, height=30,
            )
            minus_btn.on_click = (
                lambda e, rt=rtype: self._combo_adjust(
                    rt, -1,
                )
            )
            row.add(minus_btn)

            count_lbl = arcade.gui.UILabel(
                text="0", font_size=13, width=30,
                text_color=arcade.color.GOLD,
            )
            self._count_labels[rtype] = count_lbl
            row.add(count_lbl)

            plus_btn = arcade.gui.UIFlatButton(
                text="+", width=40, height=30,
            )
            plus_btn.on_click = (
                lambda e, rt=rtype: self._combo_adjust(
                    rt, 1,
                )
            )
            row.add(plus_btn)
            v_box.add(row)

        self._total_label = arcade.gui.UILabel(
            text=f"Total: 0 / {self.total}",
            font_size=13,
            text_color=arcade.color.GOLD,
        )
        v_box.add(self._total_label)

        self._confirm_btn = arcade.gui.UIFlatButton(
            text="Confirm", width=320, height=35,
        )
        self._confirm_btn.on_click = (
            lambda e: self._do_select()
        )
        v_box.add(self._confirm_btn)

        self._mount(v_box)

    def _combo_adjust(
        self, rtype: str, delta: int,
    ) -> None:
        current_val = self._selection.get(rtype, 0)
        new_val = current_val + delta
        if new_val < 0:
            return
        current_total = sum(self._selection.values())
        new_total = current_total + delta
        if new_total > self.total:
            return
        self._selection[rtype] = new_val
        if rtype in self._count_labels:
            self._count_labels[rtype].text = str(new_val)
        if self._total_label:
            self._total_label.text = (
                f"Total: {new_total} / {self.total}"
            )

    def _add_header(
        self, v_box: arcade.gui.UIBoxLayout,
    ) -> None:
        title_lbl = arcade.gui.UILabel(
            text=self.title,
            font_size=16,
            text_color=arcade.color.WHITE,
        )
        v_box.add(title_lbl)
        desc_lbl = arcade.gui.UILabel(
            text=self.description,
            font_size=12,
            text_color=arcade.color.LIGHT_GRAY,
        )
        v_box.add(desc_lbl)

    def _mount(
        self, v_box: arcade.gui.UIBoxLayout,
    ) -> None:
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

    def _do_select(self) -> None:
        chosen = {
            k: v for k, v in self._selection.items()
        }
        self.hide()
        self.on_select(self.prompt_id, chosen)

    def hide(self) -> None:
        if self._widget:
            self.ui.remove(self._widget)
            self._widget = None
        self._count_labels.clear()
        self._total_label = None
        self._confirm_btn = None


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
