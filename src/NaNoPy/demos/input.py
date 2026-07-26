from sdl2 import SDL_Event

from NaNoPy import Canvas, Color, Writer
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

    def press_left(_: SDL_Event) -> None:
        _press("left")

    def press_right(_: SDL_Event) -> None:
        _press("right")

    def release_left(_: SDL_Event) -> None:
        _release("left")

    def release_right(_: SDL_Event) -> None:
        _release("right")

    # Simplest form: bind one key to a callback. Every callback receives the
    # SDL event; name it ``_event`` when the callback does not need it.
    listener = KeyListener(name="move")
    listener.bind("space", lambda _event: print("Space pressed"))

    # For continuous movement, bind press and release handlers in a batch.
    listener.bind_many(
        {
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
