from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from sdl2 import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_Event,
    SDLK_DOWN,
    SDLK_ESCAPE,
    SDLK_LALT,
    SDLK_LCTRL,
    SDLK_LEFT,
    SDLK_LSHIFT,
    SDLK_RETURN,
    SDLK_RIGHT,
    SDLK_SPACE,
    SDLK_TAB,
    SDLK_UP,
)


KeyHandler = Callable[[SDL_Event], None]


@dataclass
class KeyBinding:
    """Container for press/release callbacks for a single key."""

    on_press: KeyHandler | None = None
    on_release: KeyHandler | None = None


COMMON_KEYS: dict[str, int] = {
    "left": SDLK_LEFT,
    "arrowleft": SDLK_LEFT,
    "right": SDLK_RIGHT,
    "arrowright": SDLK_RIGHT,
    "up": SDLK_UP,
    "arrowup": SDLK_UP,
    "down": SDLK_DOWN,
    "arrowdown": SDLK_DOWN,
    "space": SDLK_SPACE,
    "spacebar": SDLK_SPACE,
    "enter": SDLK_RETURN,
    "return": SDLK_RETURN,
    "esc": SDLK_ESCAPE,
    "escape": SDLK_ESCAPE,
    "tab": SDLK_TAB,
    "shift": SDLK_LSHIFT,
    "ctrl": SDLK_LCTRL,
    "control": SDLK_LCTRL,
    "alt": SDLK_LALT,
}


class KeyListener:
    """
    Beginner-friendly keyboard listener.

    Example:
        listener = KeyListener(
            bindings={
                "left": (on_left_down, on_key_up),
                "space": (on_space_down, None),
            },
        )
    """

    def __init__(
        self,
        bindings: Mapping[str | int, KeyBinding | tuple[KeyHandler | None, KeyHandler | None]] | None = None,
        name: str = "keyboard",
    ):
        self.name = name
        self._bindings: dict[int, KeyBinding] = {}

        if bindings:
            self.bind_many(bindings)

    def bind(
        self,
        key: str | int,
        on_press: KeyHandler | None = None,
        on_release: KeyHandler | None = None,
    ) -> "KeyListener":
        keycode = self._resolve_key(key)

        if on_press is None and on_release is None:
            raise ValueError("Provide at least one callback for a key binding.")

        self._bindings[keycode] = KeyBinding(on_press=on_press, on_release=on_release)
        return self

    def bind_many(
        self,
        bindings: Mapping[str | int, KeyBinding | tuple[KeyHandler | None, KeyHandler | None]],
    ) -> "KeyListener":
        for key, value in bindings.items():
            if isinstance(value, KeyBinding):
                self.bind(key, value.on_press, value.on_release)
            else:
                on_press, on_release = value
                self.bind(key, on_press, on_release)

        return self

    def run(self, event: SDL_Event) -> None:
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        callback_pair = self._bindings.get(int(event.key.keysym.sym))
        if callback_pair is None:
            return

        if event.type == SDL_KEYDOWN and callback_pair.on_press:
            callback_pair.on_press(event)
        elif event.type == SDL_KEYUP and callback_pair.on_release:
            callback_pair.on_release(event)

    def _resolve_key(self, key: str | int) -> int:
        if isinstance(key, int):
            return int(key)

        lowered = key.lower()

        if lowered in COMMON_KEYS:
            return int(COMMON_KEYS[lowered])

        if len(lowered) == 1:
            # SDL keycodes for letters/digits match ASCII, so ord works here.
            return ord(lowered)

        raise KeyError(f"Unknown key name '{key}'.")
