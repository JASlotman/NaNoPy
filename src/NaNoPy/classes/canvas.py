from sdl2 import SDL_CreateWindow
from sdl2 import SDL_CreateRenderer
from sdl2 import SDL_GetWindowPosition
from sdl2 import SDL_GetWindowSize

from sdl2 import SDL_WINDOWPOS_CENTERED
from sdl2 import SDL_WINDOW_HIDDEN
from sdl2 import SDL_RENDERER_SOFTWARE
from sdl2 import SDL_RENDERER_TARGETTEXTURE

from NaNoPy.custom_types import WindowType
from NaNoPy.classes.keylistener import KeyListener
from NaNoPy.classes.listener import Listener
from NaNoPy.classes.mainloop import Mainloop
from NaNoPy.constants import RENDER_FLAGS, DEFAULT_CODEC
from NaNoPy.classes.moviewriter import MovieWriter

import warnings
import ctypes
from typing import Optional

from PIL.Image import Image


class CanvasNaive:
    """NaNoPy Canvas object.

    canvas(name,xSize,ySize,*,xpos,ypos)
    name: A string that defines the made canvas, each canvas should have a unique name
    xSize: The size in x of the canvas in pixels
    ySize: the size in y of the canvas in pixels
    xpos: the x position of the window (0 is the left)
    ypos: the y position of the window (0 is the top)

    SDL is initialized lazily when a canvas is created.  Construction raises
    :class:`RuntimeError` with SDL's diagnostic when a window, renderer, or
    persistent render target cannot be created.  With the default driver,
    NaNoPy retries using SDL's software renderer when acceleration is
    unavailable (for example in many headless test environments).

    """

    def __init__(
        self,
        name: str,
        x_size: int,
        y_size: int,
        *,
        x_pos: int = -1,
        y_pos: int = -1,
        driver=-1,
        NNP: Mainloop,
    ):
        self.name = name
        self.listener: KeyListener | Listener | None = None
        self.NNP = NNP
        self.window: WindowType | None = None
        self.renderer = None
        self._reload_fonts = False
        self._persistent_texture = None
        self._window_pos_cache: tuple[int, int] | None = None
        self._window_size_cache: tuple[int, int] | None = None

        if x_pos < 0 or y_pos < 0:
            x_pos = SDL_WINDOWPOS_CENTERED
            y_pos = SDL_WINDOWPOS_CENTERED

        # Validate before SDL allocation. Overwriting the registry entry for
        # an active canvas would make its native resources unreachable.
        self.NNP._require_canvas_name_available(name)
        self.NNP.ensure_initialized()

        try:
            self.window = SDL_CreateWindow(
                str.encode(name), x_pos, y_pos, x_size, y_size, SDL_WINDOW_HIDDEN
            )
            if not self.window:
                raise RuntimeError(
                    f"Unable to create SDL window {name!r} ({x_size}x{y_size}): "
                    f"{self.NNP._sdl_error()}"
                )

            self.renderer = SDL_CreateRenderer(self.window, driver, RENDER_FLAGS)
            if not self.renderer and driver == -1:
                # The dummy/headless video backend commonly has no accelerated
                # renderer, but does provide a target-capable software renderer.
                software_flags = SDL_RENDERER_SOFTWARE | SDL_RENDERER_TARGETTEXTURE
                self.renderer = SDL_CreateRenderer(self.window, -1, software_flags)

            if not self.renderer:
                raise RuntimeError(
                    f"Unable to create SDL renderer for canvas {name!r}: "
                    f"{self.NNP._sdl_error()}"
                )

            self.NNP.ensure_persistent_texture(self)
            self.NNP.add_canvas(self)
        except Exception:
            self.NNP._destroy_canvas_resources(self)
            self.NNP.release_if_unused()
            raise

    def add_listener(self, listener: KeyListener | Listener) -> None:
        """Adds a listener object

        Listener object should have a name field
        and a method run(event) that takes the events from the screen.
        NaNoPy.classes.listener contains an abstract base class for Listener.
        """

        self.listener = listener
        self.NNP.add_listener(listener)

    def addlistener(self, listener: KeyListener | Listener) -> None:
        """(deprecated, use add_listener() instead)
        Adds a listener object

        Listener object should have a name field
        and a method run(event) that takes the events from the screen
        """
        warnings.warn(
            "addlistener() is deprecated and will be removed in a future version. "
            "Use add_listener() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_listener(listener)

    def update(self) -> bool:
        """Present the canvas and return ``False`` once its window closes."""

        return self.NNP.update(self)

    def update_embedded(self) -> Image:
        """Capture the canvas, returning a black final frame after closure."""

        return self.NNP.update_embedded(self)

    def clear(self) -> bool:
        """Clear the canvas, returning ``False`` after its window closes."""

        return self.NNP.clear(self)

    def pause(self, time) -> None:
        """Pause the canvas for a time in ms"""
        self.NNP.pause(time)

    def keep_window(self) -> None:
        """Keep window on screen if not running any code (for showing a single screen) or finite number of frames"""
        self.NNP.keep()

    def keepwindow(self) -> None:
        """(deprecated, use keep_window() instead)
        Keep window on screen if not running any code (for showing a single screen) or finite number of frames"""

        warnings.warn(
            "keepwindow() is deprecated and will be removed in a future version. "
            "Use keep_window() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.keep_window()

    def running(self) -> bool:
        """method returning if a process is running in the canvas, returns false if window is closed"""
        return self.NNP.running

    def get_window_pos(self) -> tuple[int, int]:
        """Return the current position, or the last known position after close."""

        if not self.NNP._canvas_is_active(self):
            return self._window_pos_cache or (-1, -1)

        x_pos = ctypes.c_int()
        y_pos = ctypes.c_int()

        SDL_GetWindowPosition(self.window, x_pos, y_pos)

        self._window_pos_cache = (x_pos.value, y_pos.value)
        return self._window_pos_cache

    def get_window_size(self) -> tuple[int, int]:
        """Get the size of the active window"""

        if self._window_size_cache is not None:
            return self._window_size_cache

        if not self.NNP._canvas_is_active(self):
            return (0, 0)

        x_size = ctypes.c_int()
        y_size = ctypes.c_int()

        SDL_GetWindowSize(self.window, ctypes.byref(x_size), ctypes.byref(y_size))

        self._window_size_cache = (x_size.value, y_size.value)

        return self._window_size_cache

    def start_recording(
        self, output_path: str, fps: int = 30, codec: str = DEFAULT_CODEC
    ) -> MovieWriter:
        """Start recording animation frames to MP4.

        Args:
            output_path (str): Where to save the MP4 file
            fps (int): Frames per second for output video (default: 30)
            codec (str): FFmpeg video encoder selected before frames arrive

        Returns:
            MovieWriter: The movie writer object

        Example:
            >>> canvas = Canvas("my_window", 800, 600)
            >>> movie = canvas.start_recording("animation.mp4", fps=30)
            >>> # ... animation loop ...
            >>> canvas.stop_recording()  # Finalizes the FFmpeg stream
            >>> canvas.save_recording()  # Publishes the finished MP4
        """
        return self.NNP.start_recording(output_path, fps, codec)

    def stop_recording(self) -> Optional[MovieWriter]:
        """Stop accepting frames and finalize the FFmpeg stream."""
        return self.NNP.stop_recording()

    def save_recording(self, codec: Optional[str] = None) -> Optional[str]:
        """Publish the finalized recording as MP4.

        Args:
            codec (str): Compatibility check for the codec selected at start

        Returns:
            str: Path to saved MP4 file, or None if no recording
        """
        return self.NNP.save_recording(codec)

    def get_movie_writer(self) -> Optional[MovieWriter]:
        """Get the current movie writer object (for advanced usage)."""
        return self.NNP.get_movie_writer()
