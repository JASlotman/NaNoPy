from NaNoPy import Canvas, Writer, Color
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDL_KEYUP
from sdl2 import SDL_Event

from NaNoPy.classes import Listener


class LeftRightListener(Listener):
    def __init__(self, name: str):
        super().__init__(name)
        self.dx = 0

    def run(self, event: SDL_Event) -> None:
        if event.type == SDL_KEYDOWN:
            if event.key.keysym.sym == SDLK_RIGHT:
                self.dx = 3
            elif event.key.keysym.sym == SDLK_LEFT:
                self.dx = -3
        elif event.type == SDL_KEYUP:
            if event.key.keysym.sym in (SDLK_RIGHT, SDLK_LEFT):
                self.dx = 0


def demo() -> None:
    x_size = 800
    y_size = 600

    screen = Canvas("Input Demo", x_size, y_size)
    p = Writer(screen)

    listener = LeftRightListener("move")
    screen.add_listener(listener)

    width = 50
    height = 10
    x = x_size / 2 - width / 2
    y = y_size / 2 - height / 2

    while screen.running():
        x += listener.dx
        p.draw_rectangle(x, y, width, height, Color.white, True)
        screen.update()
        screen.pause(12)
        screen.clear()


if __name__ == "__main__":
    demo()
