from NaNoPy import Canvas, Writer, Color
from NaNoPy.classes import KeyListener


def demo() -> None:
    x_size = 800
    y_size = 600

    screen = Canvas("Input Demo", x_size, y_size)
    p = Writer(screen)

    dx = 0
    pressed: set[str] = set()

    def _apply_state() -> None:
        nonlocal dx
        if "left" in pressed and "right" in pressed:
            dx = 0
        elif "left" in pressed:
            dx = -3
        elif "right" in pressed:
            dx = 3
        else:
            dx = 0

    def _press(direction: str) -> None:
        pressed.add(direction)
        _apply_state()

    def _release(direction: str) -> None:
        pressed.discard(direction)
        _apply_state()

    def press_left(_):
        _press("left")

    def press_right(_):
        _press("right")

    def release_left(_):
        _release("left")

    def release_right(_):
        _release("right")

    listener = KeyListener(
        name="move",
        bindings={
            "left": (press_left, release_left),
            "right": (press_right, release_right),
            "a": (lambda _: _press("left"), lambda _: _release("left")),
            "d": (lambda _: _press("right"), lambda _: _release("right")),
        },
    )
    screen.add_listener(listener)

    width = 50
    height = 10
    x = x_size / 2 - width / 2
    y = y_size / 2 - height / 2

    while screen.running():
        x += dx
        p.draw_rectangle(x, y, width, height, Color.white, True)
        screen.update()
        screen.pause(12)
        screen.clear()


if __name__ == "__main__":
    demo()
