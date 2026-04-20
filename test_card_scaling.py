"""Quick test: display cards that scale with the window."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import arcade
import arcade.text

arcade.text.DEFAULT_FONT_NAMES = ("Arial",)

CARD_IMAGES = [
    "client/assets/card_images/intrigue/intrigue_001.png",
    "client/assets/card_images/intrigue/intrigue_002.png",
    "client/assets/card_images/intrigue/intrigue_003.png",
    "client/assets/card_images/intrigue/intrigue_004.png",
    "client/assets/card_images/quests/contract_funk_001.png",
]

NATIVE_CARD_WIDTH = 190
NATIVE_CARD_HEIGHT = 230


class CardScalingTest(arcade.Window):
    def __init__(self):
        super().__init__(1024, 768, "Card Scaling Test", resizable=True)
        self.sprites = arcade.SpriteList()
        self.textures: list[arcade.Texture] = []
        for path in CARD_IMAGES:
            if Path(path).exists():
                tex = arcade.load_texture(path)
                self.textures.append(tex)
                sprite = arcade.Sprite(tex)
                self.sprites.append(sprite)
        self._layout()

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self._layout()

    def _layout(self) -> None:
        w, h = self.width, self.height
        n = len(self.sprites)
        if n == 0:
            return

        padding = 40
        available_w = w - padding * 2
        available_h = h - 120

        max_card_w = available_w / n - 15
        scale_by_w = max_card_w / NATIVE_CARD_WIDTH

        max_card_h = available_h
        scale_by_h = max_card_h / NATIVE_CARD_HEIGHT

        scale = min(scale_by_w, scale_by_h, 2.0)
        scale = max(scale, 0.3)

        card_w = NATIVE_CARD_WIDTH * scale
        spacing = card_w + 15
        total = n * spacing
        start_x = w / 2 - total / 2 + spacing / 2

        for i, sprite in enumerate(self.sprites):
            sprite.scale = scale
            sprite.position = (start_x + i * spacing, h / 2 + 10)

    def on_draw(self) -> None:
        self.clear(color=(40, 40, 40))
        self.sprites.draw()

        arcade.Text(
            f"Window: {self.width}x{self.height}  |  "
            f"Scale: {self.sprites[0].scale[0]:.2f}x  |  "
            f"Resize the window to test",
            self.width / 2, 30,
            arcade.color.WHITE, 14,
            anchor_x="center", anchor_y="center",
        ).draw()


def main():
    CardScalingTest()
    arcade.run()


if __name__ == "__main__":
    main()
