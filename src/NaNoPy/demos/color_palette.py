"""Overview of every named color NaNoPy ships with.

Run it with ``python -m NaNoPy.demos.color_palette`` or::

    from NaNoPy.demos import color_palette
    color_palette()
"""

from math import ceil

from NaNoPy import Canvas, Color, Writer


def _draw_checkerboard(
    writer: Writer,
    width: int,
    height: int,
    tile_size: int = 8,
) -> None:
    """Draw an 8-by-8-pixel transparency-style contrast background."""
    shades = (Color.custom(r=96, g=96, b=96), Color.custom(r=160, g=160, b=160))
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            shade = shades[(x // tile_size + y // tile_size) % 2]
            writer.draw_rectangle(x, y, tile_size, tile_size, shade, filled=True)


def _draw_text_with_stroke(
    writer: Writer,
    x: float,
    y: float,
    text: str,
    color: Color = Color.white,
    stroke_color: Color = Color.black,
) -> None:
    """Draw bitmap text with a one-pixel outline for contrast."""
    for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
        writer.draw_string(x + dx, y + dy, stroke_color, text)
    writer.draw_string(x, y, color, text)


def demo() -> None:
    """Display every color exposed by NaNoPy's built-in palette."""
    colors = list(Color.named_colors().items())
    x_size = 1000
    y_size = 600
    screen = Canvas("Color Palette", x_size, y_size)
    writer = Writer(screen)
    _draw_checkerboard(writer, x_size, y_size)

    cols = 4
    cell_w = x_size / cols
    cell_h = 120
    rows = ceil(len(colors) / cols)
    margin_y = (y_size - rows * cell_h) / 2

    for index, (name, color) in enumerate(colors):
        row = index // cols
        col = index % cols

        x = col * cell_w + 40
        y = margin_y + row * cell_h + 20

        _draw_text_with_stroke(writer, x, y + cell_h - 40, name)
        writer.draw_rectangle(x, y, cell_w - 80, cell_h - 60, color, True)

    screen.update()
    screen.keep_window()


if __name__ == "__main__":
    demo()
