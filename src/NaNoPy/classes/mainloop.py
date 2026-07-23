from sdl2 import SDL_Event

from sdl2 import SDL_Init
from sdl2 import SDL_GetWindowFlags
from sdl2 import SDL_RenderReadPixels
from sdl2 import SDL_GetError
from sdl2 import SDL_ShowWindow
from sdl2 import SDL_RenderPresent
from sdl2 import SDL_PollEvent
from sdl2 import SDL_SetRenderDrawColor
from sdl2 import SDL_RenderClear
from sdl2 import SDL_Delay
from sdl2 import SDL_DestroyWindow
from sdl2 import SDL_Quit
from sdl2 import SDL_DestroyTexture
from sdl2 import SDL_CreateTexture
from sdl2 import SDL_SetRenderTarget
from sdl2 import SDL_RenderCopy
from sdl2 import SDL_SetTextureBlendMode

from sdl2 import SDL_INIT_VIDEO
from sdl2 import SDL_WINDOW_HIDDEN
from sdl2 import SDL_WINDOWEVENT
from sdl2 import SDL_WINDOWEVENT_CLOSE
from sdl2 import SDL_WINDOWEVENT_RESIZED
from sdl2 import SDL_PIXELFORMAT_RGBA32
from sdl2 import SDL_PIXELFORMAT_RGBA8888
from sdl2 import SDL_TEXTUREACCESS_TARGET
from sdl2 import SDL_BLENDMODE_BLEND

from sdl2.sdlgfx import gfxPrimitivesSetFont

import ctypes
import signal
import threading
import warnings
from typing import Optional, TYPE_CHECKING

from NaNoPy.classes.keylistener import KeyListener
from NaNoPy.classes.listener import Listener
from NaNoPy.classes.moviewriter import MovieWriter
from NaNoPy.constants import DEFAULT_CODEC

from PIL import Image

if TYPE_CHECKING:
    from NaNoPy.classes.canvas import CanvasNaive


class Mainloop:
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO)
        self.event = SDL_Event()
        self.running: bool = True
        self.canvasses: dict[str, CanvasNaive] = {}
        self.listeners: dict[str, KeyListener | Listener] = {}

        self.multiple_windows = False
        self._persistent_textures: dict[str, ctypes.c_void_p] = {}
        self._movie_writer: Optional[MovieWriter] = None

        # Python only permits signal registration on the main thread. Preserve
        # master's graceful-shutdown behavior without making worker-thread
        # imports fail.
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGTERM, self._handle_quit)
            signal.signal(signal.SIGINT, self._handle_quit)

    def _handle_quit(self, sig_num, _frame):
        self.stop()
        raise SystemExit(sig_num)

    def add_canvas(self, canvas: "CanvasNaive"):
        self.canvasses[canvas.name] = canvas

        # Don't check it during runtime to reduce accession
        if len(self.canvasses) > 1:
            self.multiple_windows = True

    def update(self, canvas: "CanvasNaive"):
        window = canvas.window
        ren = canvas.renderer

        flags = SDL_GetWindowFlags(window)
        if (flags & SDL_WINDOW_HIDDEN):
            SDL_ShowWindow(window)

        if self.multiple_windows and canvas._reload_fonts:
            gfxPrimitivesSetFont(None, 0, 0)
            canvas._reload_fonts = False

        texture = self._copy_persistent_texture(canvas)
        SDL_RenderPresent(ren)
        if texture:
            SDL_SetRenderTarget(ren, texture)

        self._handle_events()

    def update_embedded(self, canvas: "CanvasNaive") -> Image.Image:
        if Image is None:
            raise RuntimeError("Embedded rendering requires Pillow to be installed")

        ren = canvas.renderer

        if self.multiple_windows and canvas._reload_fonts:
            gfxPrimitivesSetFont(None, 0, 0)
            canvas._reload_fonts = False

        self._handle_events()

        x_size, y_size = canvas.get_window_size()

        try:
            # RGBA32 is defined in byte order, so this stays portable across
            # CPU endianness. Copy renderer data directly into Pillow instead
            # of encoding and then decoding a PNG for every frame.
            pitch = x_size * 4
            pixels = (ctypes.c_ubyte * (pitch * y_size))()
            result = SDL_RenderReadPixels(
                ren,
                None,
                SDL_PIXELFORMAT_RGBA32,
                pixels,
                pitch,
            )
            if result != 0:
                error = SDL_GetError()
                if isinstance(error, bytes):
                    detail = error.decode(errors="replace")
                else:
                    detail = str(error) if error else "unknown SDL error"
                raise RuntimeError(f"SDL_RenderReadPixels failed: {detail}")

            img = Image.frombytes(
                "RGBA",
                (x_size, y_size),
                bytes(pixels),
                "raw",
                "RGBA",
                pitch,
                1,
            )

        except Exception as e:
            print(f"Failed to save frame: {e}")
            # Return black image on error
            return Image.new("RGBA", (x_size, y_size), (0, 0, 0, 255))

        # Keep encoder failures outside the rendering fallback. A broken FFmpeg
        # pipe must reach the caller instead of looking like a recoverable image
        # conversion failure.
        if self._movie_writer and self._movie_writer.is_recording:
            self._movie_writer.add_frame(img)

        return img


    def _handle_events(self):
        while SDL_PollEvent(ctypes.byref(self.event)) != 0:
            if (self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_CLOSE):
                self.stop()

            if (self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_RESIZED):
                for canvas in self.canvasses.values():
                    canvas._window_size_cache = None

            for listener in self.listeners.values():
                listener.run(self.event) 

    def clear(self, canvas: "CanvasNaive"):
        SDL_SetRenderDrawColor(canvas.renderer, 0, 0, 0, 255)
        SDL_RenderClear(canvas.renderer)

    def pause(self, time):
        SDL_Delay(time)

    def start_recording(
        self, output_path: str, fps: int = 30, codec: str = DEFAULT_CODEC
    ) -> MovieWriter:
        """Start recording animation frames to MP4.
        
        Args:
            output_path (str): Where to save the MP4 file
            fps (int): Frames per second for output video (default: 30)
            codec (str): FFmpeg video encoder selected before frames arrive
        
        Returns:
            MovieWriter: The movie writer object (also stored internally)
        """
        if self._movie_writer:
            if self._movie_writer.is_recording:
                raise RuntimeError("A recording is already active.")
            if self._movie_writer.has_pending_output():
                raise RuntimeError("Save or clear the previous recording before starting another.")

        self._movie_writer = MovieWriter(output_path, fps, codec)
        self._movie_writer.start_recording()
        return self._movie_writer
    
    def stop_recording(self) -> Optional[MovieWriter]:
        """Stop accepting frames and finalize the FFmpeg stream."""
        if self._movie_writer:
            self._movie_writer.stop_recording()
            return self._movie_writer
        return None
    
    def save_recording(self, codec: Optional[str] = None) -> Optional[str]:
        """Publish the finalized recording as MP4.
        
        Args:
            codec (str): Compatibility check for the codec selected at start
        
        Returns:
            str: Path to saved MP4 file, or None if no recording
        """
        if self._movie_writer:
            path = self._movie_writer.save(codec)
            self._movie_writer = None
            return str(path)
        return None
    
    def get_movie_writer(self) -> Optional[MovieWriter]:
        """Get the current movie writer object (useful for advanced usage)."""
        return self._movie_writer

    def stop(self):
        if not self.running:
            return
        self.running = False

        try:
            if self._movie_writer and self._movie_writer.is_recording:
                self._movie_writer.stop_recording()
        finally:
            for canvas in self.canvasses.values():
                SDL_DestroyTexture(canvas._persistent_texture)
                SDL_DestroyWindow(canvas.window)

            SDL_Quit()

    def keep(self):
        while self.running:
            while SDL_PollEvent(ctypes.byref(self.event)) != 0:
                if (
                    self.event.type == SDL_WINDOWEVENT
                    and self.event.window.event == SDL_WINDOWEVENT_CLOSE
                ):
                    self.stop()

    def add_listener(self, listener: KeyListener | Listener) -> None:
        self.listeners[listener.name] = listener

    def addlistener(self, listener: KeyListener | Listener) -> None:
        """Deprecated alias for :meth:`add_listener`."""
        warnings.warn(
            "addlistener() is deprecated and will be removed in a future version. "
            "Use add_listener() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_listener(listener)

    def ensure_persistent_texture(self, canvas: "CanvasNaive"):
        texture = canvas._persistent_texture

        # If texture exist already return
        if texture:
            return texture

        x_size, y_size = canvas.get_window_size()

        texture = SDL_CreateTexture(
            canvas.renderer,
            SDL_PIXELFORMAT_RGBA8888,
            SDL_TEXTUREACCESS_TARGET,
            x_size,
            y_size,
        )

        # Set blending mode to alpha blending
        # This ensures overlapping textures render correctly
        SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND)
    
        canvas._persistent_texture = texture

        SDL_SetRenderTarget(canvas.renderer, texture)
        SDL_SetRenderDrawColor(canvas.renderer, 0, 0, 0, 255)
        SDL_RenderClear(canvas.renderer)

        return texture

    def _copy_persistent_texture(self, canvas: "CanvasNaive") -> Optional[ctypes.c_void_p]:
        texture = canvas._persistent_texture

        if not texture:
            return None
        
        SDL_SetRenderTarget(canvas.renderer, None)
        SDL_RenderCopy(canvas.renderer, texture, None, None)

        return texture
