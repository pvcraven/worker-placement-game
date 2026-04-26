"""Modal dialogs for card selection, building purchase, etc."""

from __future__ import annotations

import logging
from pathlib import Path

import arcade
import arcade.gui

from shared.constants import RESOURCE_SYMBOLS

_log = logging.getLogger(__name__)


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

    def show(
        self,
        window_width: float,
        window_height: float,
        scale: float = 1.0,
    ) -> None:
        s = scale
        v_box = arcade.gui.UIBoxLayout(space_between=int(8 * s))

        label = arcade.gui.UILabel(
            text=self.title,
            font_size=max(8, int(16 * s)),
            text_color=arcade.color.WHITE,
        )
        v_box.add(label)

        for card in self.cards[:8]:
            name = card.get("name", "???")
            card_id = card.get("id", "")
            btn = arcade.gui.UIFlatButton(
                text=name,
                width=int(280 * s),
                height=int(35 * s),
            )
            btn.on_click = lambda event, cid=card_id: self._select(cid)
            v_box.add(btn)

        cancel_btn = arcade.gui.UIFlatButton(
            text="Cancel",
            width=int(280 * s),
            height=int(35 * s),
        )
        cancel_btn.on_click = lambda event: self._cancel()
        v_box.add(cancel_btn)

        bg_box = v_box.with_padding(all=int(20 * s)).with_background(color=(0, 0, 0))
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


_CARD_SPACING = 205


class CardSpriteSelectionDialog:
    """A card selection overlay that shows full card images."""

    def __init__(
        self,
        title: str,
        cards: list[dict],
        card_type: str,
        on_select: callable,
        on_cancel: callable | None = None,
        cancel_label: str = "Cancel",
        highlight_card_id: str | None = None,
        highlight_text: str = "",
    ) -> None:
        self.title = title
        self.cards = cards[:6]
        self.card_type = card_type
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.cancel_label = cancel_label
        self.highlight_card_id = highlight_card_id
        self.highlight_text = highlight_text
        self._sprite_list: arcade.SpriteList | None = None
        self._card_ids: list[str] = []
        self._panel_rect: tuple[float, float, float, float] = (0, 0, 0, 0)
        self._cancel_rect: tuple[float, float, float, float] = (0, 0, 0, 0)
        self._last_draw_key: tuple = ()

    def draw(
        self,
        w: float,
        h: float,
        scale: float = 1.0,
    ) -> None:
        s = scale
        spacing = _CARD_SPACING * s
        card_count = max(len(self.cards), 1)
        needed_w = card_count * spacing + 40 * s
        panel_w = max(min(w - 40 * s, needed_w), 300 * s)
        panel_h = 390 * s
        px, py = w / 2, h / 2
        self._panel_rect = (px, py, panel_w, panel_h)

        arcade.draw_rect_filled(
            arcade.rect.XYWH(px, py, panel_w, panel_h),
            (0, 0, 0, 230),
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(px, py, panel_w, panel_h),
            arcade.color.WHITE,
            border_width=2,
        )

        title_obj = arcade.Text(
            self.title,
            px,
            py + panel_h / 2 - 20 * s,
            arcade.color.WHITE,
            max(8, int(16 * s)),
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        title_obj.draw()

        if not self.cards:
            empty = arcade.Text(
                "No cards",
                px,
                py,
                arcade.color.LIGHT_GRAY,
                max(8, int(14 * s)),
                anchor_x="center",
                anchor_y="center",
            )
            empty.draw()
        else:
            total = len(self.cards) * spacing
            start_x = px - total / 2 + spacing / 2
            positions = [
                (start_x + i * spacing, py + 10 * s) for i in range(len(self.cards))
            ]

            draw_key = (w, h, s)
            if self._sprite_list is None or self._last_draw_key != draw_key:
                self._last_draw_key = draw_key
                self._card_ids = []
                self._sprite_list = arcade.SpriteList()
                for card, (cx, cy) in zip(self.cards, positions):
                    card_id = card.get("id", "")
                    self._card_ids.append(card_id)
                    png_path = Path(
                        f"client/assets/card_images/{self.card_type}/{card_id}.png"
                    )
                    if not png_path.exists():
                        _log.warning("Card image not found: %s", png_path)
                        continue
                    sprite = arcade.Sprite(str(png_path))
                    png_scale = 0.5 if self.card_type in ("quests", "intrigue") else 1.0
                    sprite.scale = s * png_scale
                    sprite.position = (cx, cy)
                    self._sprite_list.append(sprite)
            self._sprite_list.draw()

            if self.highlight_card_id and self.highlight_text:
                for card, (cx, cy) in zip(self.cards, positions):
                    if card.get("id") == self.highlight_card_id:
                        png_scale = (
                            0.5
                            if self.card_type in ("quests", "intrigue")
                            else 1.0
                        )
                        card_h = 350 * s * png_scale
                        bonus_label = arcade.Text(
                            self.highlight_text,
                            cx,
                            cy - card_h / 2 - 14 * s,
                            arcade.color.GOLD,
                            max(8, int(13 * s)),
                            anchor_x="center",
                            anchor_y="center",
                            bold=True,
                        )
                        bonus_label.draw()
                        break

        hint = arcade.Text(
            "Click a card to select it",
            px,
            py - panel_h / 2 + 55 * s,
            arcade.color.GOLD,
            max(8, int(13 * s)),
            anchor_x="center",
            anchor_y="center",
        )
        hint.draw()

        cancel_w, cancel_h = int(120 * s), int(32 * s)
        cancel_x = px
        cancel_y = py - panel_h / 2 + 25 * s
        self._cancel_rect = (cancel_x, cancel_y, cancel_w, cancel_h)
        arcade.draw_rect_filled(
            arcade.rect.XYWH(cancel_x, cancel_y, cancel_w, cancel_h),
            (44, 62, 80),
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cancel_x, cancel_y, cancel_w, cancel_h),
            arcade.color.WHITE,
            border_width=1,
        )
        cancel_text = arcade.Text(
            self.cancel_label,
            cancel_x,
            cancel_y,
            arcade.color.WHITE,
            max(8, int(14 * s)),
            anchor_x="center",
            anchor_y="center",
        )
        cancel_text.draw()

    def on_click(self, x: float, y: float) -> bool:
        cx, cy, cw, ch = self._cancel_rect
        if abs(x - cx) <= cw / 2 and abs(y - cy) <= ch / 2:
            if self.on_cancel:
                self.on_cancel()
            return True

        if self._sprite_list:
            hits = arcade.get_sprites_at_point((x, y), self._sprite_list)
            if hits:
                idx = self._sprite_list.index(hits[0])
                if idx < len(self._card_ids):
                    self.on_select(self._card_ids[idx])
                    return True

        return False


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

    def show(
        self,
        window_width: float,
        window_height: float,
        scale: float = 1.0,
    ) -> None:
        s = scale
        v_box = arcade.gui.UIBoxLayout(space_between=int(8 * s))

        label = arcade.gui.UILabel(
            text="Real Estate Listings",
            font_size=max(8, int(16 * s)),
            text_color=arcade.color.WHITE,
        )
        v_box.add(label)

        coins_label = arcade.gui.UILabel(
            text=f"Your coins: {self.player_coins}",
            font_size=max(8, int(13 * s)),
            text_color=arcade.color.GOLD,
        )
        v_box.add(coins_label)

        btn_w = int(400 * s)
        btn_h = int(35 * s)
        if not self.buildings:
            empty_label = arcade.gui.UILabel(
                text="No buildings available for purchase.",
                font_size=max(8, int(13 * s)),
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

                reward = building.get("visitor_reward", {})
                reward_parts = []
                for key, sym in RESOURCE_SYMBOLS:
                    val = reward.get(key, 0)
                    if val > 0:
                        reward_parts.append(f"{val}{sym}")
                reward_str = " ".join(reward_parts) if reward_parts else "Special"

                btn_text = f"{name} | {cost}$ | {vp}VP | {reward_str}"
                if not can_afford:
                    btn_text = f"[Can't afford] {btn_text}"

                btn = arcade.gui.UIFlatButton(
                    text=btn_text,
                    width=btn_w,
                    height=btn_h,
                )
                if can_afford:
                    btn.on_click = lambda event, b=bid: self._purchase(b)
                else:
                    btn.on_click = lambda event: None
                v_box.add(btn)

        cancel_btn = arcade.gui.UIFlatButton(
            text="Cancel",
            width=btn_w,
            height=btn_h,
        )
        cancel_btn.on_click = lambda event: self._cancel()
        v_box.add(cancel_btn)

        bg_box = v_box.with_padding(all=int(20 * s)).with_background(color=(0, 0, 0))
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

    Thin wrapper around CardSpriteSelectionDialog.
    """

    def __init__(
        self,
        quests: list[dict],
        on_select: callable,
        on_skip: callable,
        bonus_quest_id: str | None = None,
        bonus_vp: int = 0,
    ) -> None:
        self._visible = False
        highlight_id = None
        highlight_text = ""
        if bonus_quest_id and bonus_vp > 0:
            highlight_id = bonus_quest_id
            highlight_text = f"+{bonus_vp}VP bonus"
        self._inner = CardSpriteSelectionDialog(
            title="Complete a Quest?",
            cards=quests,
            card_type="quests",
            on_select=on_select,
            on_cancel=on_skip,
            cancel_label="Skip",
            highlight_card_id=highlight_id,
            highlight_text=highlight_text,
        )

    def show(
        self,
        window_width: float,
        window_height: float,
    ) -> None:
        self._visible = True

    def draw(
        self,
        ww: float,
        wh: float,
        scale: float = 1.0,
    ) -> None:
        if not self._visible:
            return
        self._inner.draw(ww, wh, scale=scale)

    def handle_click(
        self,
        x: float,
        y: float,
    ) -> bool:
        if not self._visible:
            return False
        if self._inner.on_click(x, y):
            self._visible = False
            return True
        return False

    def hide(self) -> None:
        self._visible = False


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
        self,
        window_width: float,
        window_height: float,
        scale: float = 1.0,
    ) -> None:
        s = scale
        v_box = arcade.gui.UIBoxLayout(space_between=int(8 * s))

        label = arcade.gui.UILabel(
            text=self.title,
            font_size=max(8, int(16 * s)),
            text_color=arcade.color.WHITE,
        )
        v_box.add(label)

        desc = arcade.gui.UILabel(
            text=self.description,
            font_size=max(8, int(13 * s)),
            text_color=arcade.color.LIGHT_GRAY,
        )
        v_box.add(desc)

        btn_w = int(320 * s)
        btn_h = int(35 * s)
        for item in self.choices[:8]:
            name = item.get(self.label_key, "???")
            item_id = item.get("id", "")
            btn = arcade.gui.UIFlatButton(
                text=name,
                width=btn_w,
                height=btn_h,
            )
            btn.on_click = lambda event, cid=item_id: self._select(cid)
            v_box.add(btn)

        bg_box = v_box.with_padding(
            all=int(20 * s),
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
        self,
        window_width: float,
        window_height: float,
        scale: float = 1.0,
    ) -> None:
        s = scale
        v_box = arcade.gui.UIBoxLayout(space_between=int(8 * s))

        label = arcade.gui.UILabel(
            text=self.title,
            font_size=max(8, int(16 * s)),
            text_color=arcade.color.WHITE,
        )
        v_box.add(label)

        desc_label = arcade.gui.UILabel(
            text=self.effect_description,
            font_size=max(8, int(12 * s)),
            text_color=arcade.color.GOLD,
        )
        v_box.add(desc_label)

        btn_w = int(350 * s)
        btn_h = int(35 * s)
        if not self.eligible_targets:
            no_target_label = arcade.gui.UILabel(
                text="No opponents have the targeted resources.",
                font_size=max(8, int(13 * s)),
                text_color=arcade.color.LIGHT_GRAY,
            )
            v_box.add(no_target_label)
        else:
            for target in self.eligible_targets:
                pid = target.get("player_id", "")
                name = target.get("player_name", "???")
                res = target.get("resources", {})
                res_parts = []
                for key, sym in RESOURCE_SYMBOLS:
                    val = res.get(key, 0)
                    if val > 0:
                        res_parts.append(f"{val}{sym}")
                res_str = " ".join(res_parts) if res_parts else "no resources"
                btn_text = f"{name} ({res_str})"
                btn = arcade.gui.UIFlatButton(
                    text=btn_text,
                    width=btn_w,
                    height=btn_h,
                )
                btn.on_click = lambda event, p=pid: self._select(p)
                v_box.add(btn)

        cancel_btn = arcade.gui.UIFlatButton(
            text="Cancel",
            width=btn_w,
            height=btn_h,
        )
        cancel_btn.on_click = lambda event: self._cancel()
        v_box.add(cancel_btn)

        bg_box = v_box.with_padding(
            all=int(20 * s),
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
        self,
        window_width: float,
        window_height: float,
        scale: float = 1.0,
    ) -> None:
        self._scale = scale
        if self.choice_type == "bundle":
            self._show_bundle()
        elif self.choice_type == "combo":
            self._show_combo()
        else:
            self._show_pick()

    def _show_pick(self) -> None:
        s = getattr(self, "_scale", 1.0)
        v_box = arcade.gui.UIBoxLayout(space_between=int(8 * s))
        self._add_header(v_box)

        target = self.pick_count
        self._selection = {t: 0 for t in self.allowed_types}
        info = arcade.gui.UILabel(
            text=f"Pick {target} resource(s):",
            font_size=max(8, int(13 * s)),
            text_color=arcade.color.LIGHT_GRAY,
        )
        v_box.add(info)

        btn_w = int(320 * s)
        btn_h = int(35 * s)
        for rtype in self.allowed_types:
            label = _RESOURCE_LABELS.get(rtype, rtype)
            btn = arcade.gui.UIFlatButton(
                text=label,
                width=btn_w,
                height=btn_h,
            )
            btn.on_click = lambda e, rt=rtype: self._pick_add(rt)
            v_box.add(btn)

        self._total_label = arcade.gui.UILabel(
            text="Selected: 0 / " + str(target),
            font_size=max(8, int(13 * s)),
            text_color=arcade.color.GOLD,
        )
        v_box.add(self._total_label)

        reset_btn = arcade.gui.UIFlatButton(
            text="Reset",
            width=btn_w,
            height=int(30 * s),
        )
        reset_btn.on_click = lambda e: self._pick_reset()
        v_box.add(reset_btn)

        self._mount(v_box)

    def _pick_add(self, rtype: str) -> None:
        target = self.pick_count
        current = sum(self._selection.values())
        if current >= target:
            return
        self._selection[rtype] = self._selection.get(rtype, 0) + 1
        current += 1
        if self._total_label:
            self._total_label.text = f"Selected: {current} / {target}"
        if current == target:
            self._do_select()

    def _pick_reset(self) -> None:
        self._selection = {t: 0 for t in self.allowed_types}
        if self._total_label:
            self._total_label.text = f"Selected: 0 / {self.pick_count}"

    def _show_bundle(self) -> None:
        s = getattr(self, "_scale", 1.0)
        v_box = arcade.gui.UIBoxLayout(space_between=int(8 * s))
        self._add_header(v_box)

        btn_w = int(320 * s)
        btn_h = int(35 * s)
        for bundle in self.bundles:
            label = bundle.get("label", "???")
            res = bundle.get("resources", {})
            btn = arcade.gui.UIFlatButton(
                text=label,
                width=btn_w,
                height=btn_h,
            )
            btn.on_click = lambda e, r=res: self._bundle_select(r)
            v_box.add(btn)

        self._mount(v_box)

    def _bundle_select(self, resources: dict) -> None:
        self._selection = dict(resources)
        self._do_select()

    def _show_combo(self) -> None:
        s = getattr(self, "_scale", 1.0)
        v_box = arcade.gui.UIBoxLayout(space_between=int(8 * s))
        self._add_header(v_box)
        self._selection = {t: 0 for t in self.allowed_types}

        font_sm = max(8, int(13 * s))
        small_btn = int(40 * s)
        small_btn_h = int(30 * s)
        for rtype in self.allowed_types:
            label = _RESOURCE_LABELS.get(rtype, rtype)
            row = arcade.gui.UIBoxLayout(
                vertical=False,
                space_between=int(8 * s),
            )
            name_lbl = arcade.gui.UILabel(
                text=f"{label}:",
                font_size=font_sm,
                width=int(120 * s),
                text_color=arcade.color.WHITE,
            )
            row.add(name_lbl)

            minus_btn = arcade.gui.UIFlatButton(
                text="-",
                width=small_btn,
                height=small_btn_h,
            )
            minus_btn.on_click = lambda e, rt=rtype: self._combo_adjust(
                rt,
                -1,
            )
            row.add(minus_btn)

            count_lbl = arcade.gui.UILabel(
                text="0",
                font_size=font_sm,
                width=int(30 * s),
                text_color=arcade.color.GOLD,
            )
            self._count_labels[rtype] = count_lbl
            row.add(count_lbl)

            plus_btn = arcade.gui.UIFlatButton(
                text="+",
                width=small_btn,
                height=small_btn_h,
            )
            plus_btn.on_click = lambda e, rt=rtype: self._combo_adjust(
                rt,
                1,
            )
            row.add(plus_btn)
            v_box.add(row)

        self._total_label = arcade.gui.UILabel(
            text=f"Total: 0 / {self.total}",
            font_size=font_sm,
            text_color=arcade.color.GOLD,
        )
        v_box.add(self._total_label)

        self._confirm_btn = arcade.gui.UIFlatButton(
            text="Confirm",
            width=int(320 * s),
            height=int(35 * s),
        )
        self._confirm_btn.on_click = lambda e: self._do_select()
        v_box.add(self._confirm_btn)

        self._mount(v_box)

    def _combo_adjust(
        self,
        rtype: str,
        delta: int,
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
            self._total_label.text = f"Total: {new_total} / {self.total}"

    def _add_header(
        self,
        v_box: arcade.gui.UIBoxLayout,
    ) -> None:
        s = getattr(self, "_scale", 1.0)
        title_lbl = arcade.gui.UILabel(
            text=self.title,
            font_size=max(8, int(16 * s)),
            text_color=arcade.color.WHITE,
        )
        v_box.add(title_lbl)
        desc_lbl = arcade.gui.UILabel(
            text=self.description,
            font_size=max(8, int(12 * s)),
            text_color=arcade.color.LIGHT_GRAY,
        )
        v_box.add(desc_lbl)

    def _mount(
        self,
        v_box: arcade.gui.UIBoxLayout,
    ) -> None:
        s = getattr(self, "_scale", 1.0)
        bg_box = v_box.with_padding(
            all=int(20 * s),
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
        chosen = {k: v for k, v in self._selection.items()}
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

    def show(self, scale: float = 1.0) -> None:
        s = scale
        v_box = arcade.gui.UIBoxLayout(space_between=int(10 * s))

        label = arcade.gui.UILabel(
            text=self.message,
            font_size=max(8, int(14 * s)),
            text_color=arcade.color.WHITE,
            multiline=True,
            width=int(300 * s),
        )
        v_box.add(label)

        h_box = arcade.gui.UIBoxLayout(
            vertical=False,
            space_between=int(20 * s),
        )

        yes_btn = arcade.gui.UIFlatButton(
            text="Yes",
            width=int(120 * s),
            height=int(40 * s),
        )
        yes_btn.on_click = lambda event: self._confirm(True)
        h_box.add(yes_btn)

        no_btn = arcade.gui.UIFlatButton(
            text="No",
            width=int(120 * s),
            height=int(40 * s),
        )
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
