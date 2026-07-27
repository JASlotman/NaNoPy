from sdl2 import SDL_Event


class Listener:
    def __init__(self, name: str) -> None:
        self.name = name

    def run(self, event: SDL_Event) -> None:
        raise NotImplementedError("Extend Listener for Usability.")
