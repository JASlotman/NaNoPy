from math import ceil

from NaNoPy import Canvas, Writer, Color


COLORS = [
    ("red", Color.red),
    ("blue", Color.blue),
    ("green", Color.green),
    ("yellow", Color.yellow),
    ("magenta", Color.magenta),
    ("cyan", Color.cyan),
    ("black", Color.black),
    ("white", Color.white),
    ("gray", Color.gray),
    ("purple", Color.purple),
    ("orange", Color.orange),
    ("tangerine", Color.tangerine),
    ("lime", Color.lime),
    ("brown", Color.brown),
]


def demo() -> None:
    x_size = 1000
    y_size = 600
    screen = Canvas("Color Palette", x_size, y_size)
    writer = Writer(screen)

    cols = 4
    cell_w = x_size / cols
    cell_h = 120
    rows = ceil(len(COLORS) / cols)
    margin_y = (y_size - rows * cell_h) / 2

    for idx, (name, color) in enumerate(COLORS):
        row = idx // cols
        col = idx % cols

        x = col * cell_w + 40
        y = margin_y + row * cell_h + 20

        writer.draw_string(x, y + cell_h - 40, Color.white, name)
        writer.draw_rectangle(x, y, cell_w - 80, cell_h - 60, color, True)

    screen.update()
    screen.keep_window()


if __name__ == "__main__":
    demo()
