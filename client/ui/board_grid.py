class BoardGrid:
    """Converts grid coordinates to pixel positions within the board area.

    The board area is divided into a grid of cols x rows cells.
    Row 0 is the top of the board. Half-integer coordinates are supported.
    """

    def __init__(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        cols: int = 7,
        rows: int = 9,
        margin_pct: float = 0.06,
    ):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._cols = cols
        self._rows = rows
        self._cell_w = w / cols
        self._cell_h = h / rows
        self._margin = margin_pct * self._cell_w

    @property
    def cell_width(self) -> float:
        return self._cell_w

    @property
    def cell_height(self) -> float:
        return self._cell_h

    def cell_rect(
        self,
        col: float,
        row: float,
        col_span: float = 1.0,
        row_span: float = 1.0,
    ) -> tuple[float, float, float, float]:
        """Return (center_x, center_y, content_width, content_height).

        col/row support half-integers (e.g. 3.5, 1.5).
        Content dimensions are inset by margin on each side.
        Row 0 is the top of the board.
        """
        cx = self._x + (col + col_span / 2) * self._cell_w
        cy = self._y + self._h - (row + row_span / 2) * self._cell_h
        cw = col_span * self._cell_w - 2 * self._margin
        ch = row_span * self._cell_h - 2 * self._margin
        return cx, cy, cw, ch

    def card_scale(self, row_span: float, base_width: int, base_height: int) -> float:
        """Uniform scale factor to fit a card into cell(s).

        Fits the card within 1-column × row_span cells (minus margins),
        maintaining aspect ratio. Card images are generated at 2× the
        base constants, so we divide by 2× the base dimensions.
        """
        _, _, cw, ch = self.cell_rect(0, 0, 1.0, row_span)
        img_w = base_width * 2
        img_h = base_height * 2
        scale_w = cw / img_w
        scale_h = ch / img_h
        return min(scale_w, scale_h)

    def panel_width(self, panel_cols: int = 2) -> float:
        """Pixel width for the side panel."""
        return panel_cols * self._cell_w
