from sdl2 import SDL_Event

from sdl2 import SDL_InitSubSystem
from sdl2 import SDL_GetWindowFlags
from sdl2 import SDL_GetWindowFromID
from sdl2 import SDL_GetWindowID
from sdl2 import SDL_RenderReadPixels
from sdl2 import SDL_GetError
from sdl2 import SDL_ShowWindow
from sdl2 import SDL_RenderPresent
from sdl2 import SDL_PollEvent
from sdl2 import SDL_PushEvent
from sdl2 import SDL_SetRenderDrawColor
from sdl2 import SDL_RenderClear
from sdl2 import SDL_Delay
from sdl2 import SDL_DestroyWindow
from sdl2 import SDL_QuitSubSystem
from sdl2 import SDL_DestroyTexture
from sdl2 import SDL_DestroyRenderer
from sdl2 import SDL_CreateTexture
from sdl2 import SDL_SetRenderTarget
from sdl2 import SDL_RenderCopy
from sdl2 import SDL_SetTextureBlendMode

from sdl2 import SDL_INIT_VIDEO
from sdl2 import SDL_WINDOW_HIDDEN
from sdl2 import SDL_WINDOWEVENT
from sdl2 import SDL_WINDOWEVENT_CLOSE
from sdl2 import SDL_WINDOWEVENT_RESIZED
from sdl2 import SDL_KEYDOWN
from sdl2 import SDL_KEYUP
from sdl2 import SDL_TEXTEDITING
from sdl2 import SDL_TEXTINPUT
from sdl2 import SDL_MOUSEMOTION
from sdl2 import SDL_MOUSEBUTTONDOWN
from sdl2 import SDL_MOUSEBUTTONUP
from sdl2 import SDL_MOUSEWHEEL
from sdl2 import SDL_DROPFILE
from sdl2 import SDL_DROPTEXT
from sdl2 import SDL_DROPBEGIN
from sdl2 import SDL_DROPCOMPLETE
from sdl2 import SDL_USEREVENT
from sdl2 import SDL_LASTEVENT
from sdl2 import SDL_PIXELFORMAT_RGBA32
from sdl2 import SDL_PIXELFORMAT_RGBA8888
from sdl2 import SDL_TEXTUREACCESS_TARGET
from sdl2 import SDL_BLENDMODE_BLEND

from sdl2.sdlgfx import gfxPrimitivesSetFont

import ctypes
import threading
import warnings
from typing import Optional, TYPE_CHECKING

from NaNoPy.classes.keylistener import KeyListener
from NaNoPy.classes.listener import Listener
from NaNoPy.classes.moviewriter import MovieWriter
from NaNoPy.constants import DEFAULT_CODEC

from PIL import Image

try:
    # Added in SDL 2.0.22; keep NaNoPy importable with older PySDL2 bindings.
    from sdl2 import SDL_TEXTEDITING_EXT
except ImportError:  # pragma: no cover - depends on the installed SDL bindings
    SDL_TEXTEDITING_EXT = None

if TYPE_CHECKING:
    from NaNoPy.classes.canvas import CanvasNaive


class Mainloop:
    """Coordinate SDL canvases, events, and optional movie recording.

    Creating a :class:`Mainloop` is intentionally side-effect free.  The SDL
    video subsystem is initialized lazily when the first canvas is created.
    :meth:`stop` releases those resources and resets the registries, so the
    same ``Mainloop`` can safely be reused by a later canvas (which is
    particularly important in notebooks). NaNoPy deliberately leaves process
    signal policy to the host application.
    """

    def __init__(self):
        self.event = SDL_Event()
        self.running: bool = False
        self.canvasses: dict[str, CanvasNaive] = {}
        self.listeners: dict[str, KeyListener | Listener] = {}

        self.multiple_windows = False
        self._persistent_textures: dict[str, ctypes.c_void_p] = {}
        self._movie_writer: Optional[MovieWriter] = None
        self._sdl_initialized = False
        self._runtime_thread_id: int | None = None

    @staticmethod
    def _sdl_error() -> str:
        """Return SDL's current error as readable text."""

        error = SDL_GetError()
        if isinstance(error, bytes):
            return error.decode(errors="replace") or "unknown SDL error"
        return str(error) if error else "unknown SDL error"

    def ensure_initialized(self) -> None:
        """Initialize SDL for canvas use, raising a useful error on failure.

        SDL reference-counts subsystem initialization. Every active mainloop
        acquires one video reference and :meth:`stop` releases exactly that
        reference, so independent mainloops and external SDL users cannot
        shut one another down.
        """

        if self._sdl_initialized:
            self._require_runtime_thread()
            self.running = True
            return

        if SDL_InitSubSystem(SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"Unable to initialize SDL video: {self._sdl_error()}")

        self._sdl_initialized = True
        self._runtime_thread_id = threading.get_ident()
        self.running = True

    def _require_runtime_thread(self) -> None:
        """Reject cross-thread SDL access with an actionable error.

        SDL render resources are thread-affine on several supported video
        backends. Silently tearing them down from another thread can leave
        native pointers stale or crash the host process.
        """

        if (
            self._sdl_initialized
            and self._runtime_thread_id != threading.get_ident()
        ):
            raise RuntimeError(
                "Canvas operations, including Mainloop.stop(), must run on "
                "the thread that created the first active canvas."
            )

    def _canvas_is_active(self, canvas: "CanvasNaive") -> bool:
        """Return whether a canvas can be used without touching stale pointers.

        Closing a window is normal control flow. Calls remaining in the current
        animation iteration therefore become harmless no-ops. Cross-thread SDL
        access remains a programming error and is reported explicitly.
        """

        self._require_runtime_thread()
        return bool(
            self._sdl_initialized
            and self.running
            and getattr(canvas, "window", None)
            and getattr(canvas, "renderer", None)
        )

    def _require_active_canvas(self, canvas: "CanvasNaive") -> None:
        """Require a live canvas for an operation that cannot be skipped."""

        if not self._canvas_is_active(canvas):
            raise RuntimeError("Canvas is closed and can no longer be rendered.")

    @staticmethod
    def _closed_canvas_image(canvas: "CanvasNaive") -> Image.Image:
        """Return a deterministic frame without consulting destroyed SDL data."""

        size = getattr(canvas, "_window_size_cache", None) or (1, 1)
        return Image.new("RGBA", size, (0, 0, 0, 255))

    def _owns_window_id(self, window_id: int) -> bool:
        """Return whether an SDL window ID belongs to this mainloop."""

        return any(
            canvas.window and SDL_GetWindowID(canvas.window) == window_id
            for canvas in self.canvasses.values()
        )

    @staticmethod
    def _event_window_id(event: SDL_Event) -> int:
        """Return the owning window ID for any window-scoped SDL event."""

        event_type = event.type
        if event_type == SDL_WINDOWEVENT:
            return event.window.windowID
        if event_type in (SDL_KEYDOWN, SDL_KEYUP):
            return event.key.windowID
        if event_type == SDL_TEXTEDITING:
            return event.edit.windowID
        if event_type == SDL_TEXTINPUT:
            return event.text.windowID
        if SDL_TEXTEDITING_EXT is not None and event_type == SDL_TEXTEDITING_EXT:
            return event.editExt.windowID
        if event_type == SDL_MOUSEMOTION:
            return event.motion.windowID
        if event_type in (SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP):
            return event.button.windowID
        if event_type == SDL_MOUSEWHEEL:
            return event.wheel.windowID
        if event_type in (SDL_DROPFILE, SDL_DROPTEXT, SDL_DROPBEGIN, SDL_DROPCOMPLETE):
            return event.drop.windowID
        if SDL_USEREVENT <= event_type < SDL_LASTEVENT:
            return event.user.windowID
        return 0

    def _deactivate_runtime(self) -> None:
        """Release process-level state after all canvas resources are gone."""

        if self._sdl_initialized:
            SDL_QuitSubSystem(SDL_INIT_VIDEO)
        self._sdl_initialized = False
        self._runtime_thread_id = None
        self.running = False

    def release_if_unused(self) -> None:
        """Undo lazy initialization after a first-canvas construction failure."""

        if not self.canvasses:
            self._require_runtime_thread()
            self._deactivate_runtime()

    def _require_canvas_name_available(self, name: str) -> None:
        """Reject duplicate names before they can orphan native resources."""

        self._require_runtime_thread()
        if name in self.canvasses:
            raise ValueError(
                f"A canvas named {name!r} already exists in this Mainloop. "
                "Canvas names must be unique while their windows are active."
            )

    def add_canvas(self, canvas: "CanvasNaive"):
        self._require_canvas_name_available(canvas.name)
        self.ensure_initialized()
        self.canvasses[canvas.name] = canvas

        # Don't check it during runtime to reduce accession
        if len(self.canvasses) > 1:
            self.multiple_windows = True

    def update(self, canvas: "CanvasNaive") -> bool:
        """Present one frame and return whether the mainloop remains active."""

        if not self._canvas_is_active(canvas):
            return False

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

        return self._handle_events()

    def update_embedded(self, canvas: "CanvasNaive") -> Image.Image:
        if Image is None:
            raise RuntimeError("Embedded rendering requires Pillow to be installed")

        if not self._canvas_is_active(canvas):
            return self._closed_canvas_image(canvas)

        if self.multiple_windows and canvas._reload_fonts:
            gfxPrimitivesSetFont(None, 0, 0)
            canvas._reload_fonts = False

        if not self._handle_events():
            return self._closed_canvas_image(canvas)

        # Event handlers may close canvases. Re-read the validated renderer
        # instead of retaining a native pointer across event dispatch.
        if not self._canvas_is_active(canvas):
            return self._closed_canvas_image(canvas)
        ren = canvas.renderer

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


    def _handle_events(self) -> bool:
        """Dispatch pending events and report whether rendering may continue."""

        self._require_runtime_thread()
        foreign_events: list[SDL_Event] = []
        try:
            while SDL_PollEvent(ctypes.byref(self.event)) != 0:
                window_id = self._event_window_id(self.event)
                if window_id and not self._owns_window_id(window_id):
                    # SDL has one process-wide event queue. Temporarily remove
                    # live foreign events, then restore them only after this
                    # poll pass so we cannot immediately consume the same event
                    # again or deliver it to this mainloop's listeners.
                    if SDL_GetWindowFromID(window_id):
                        event_copy = SDL_Event()
                        ctypes.memmove(
                            ctypes.byref(event_copy),
                            ctypes.byref(self.event),
                            ctypes.sizeof(SDL_Event),
                        )
                        foreign_events.append(event_copy)
                    continue

                if (
                    self.event.type == SDL_WINDOWEVENT
                    and self.event.window.event == SDL_WINDOWEVENT_CLOSE
                ):
                    self.stop()
                    return False

                if (
                    self.event.type == SDL_WINDOWEVENT
                    and self.event.window.event == SDL_WINDOWEVENT_RESIZED
                ):
                    for canvas in self.canvasses.values():
                        canvas._window_size_cache = None

                # A listener may stop the loop or change listener registration.
                # Iterate a snapshot and stop immediately after native teardown.
                for listener in list(self.listeners.values()):
                    listener.run(self.event)
                    if not self.running:
                        return False

            return self.running
        finally:
            for foreign_event in foreign_events:
                SDL_PushEvent(ctypes.byref(foreign_event))

    def clear(self, canvas: "CanvasNaive") -> bool:
        """Clear a live canvas, or do nothing after its window has closed."""

        if not self._canvas_is_active(canvas):
            return False
        SDL_SetRenderDrawColor(canvas.renderer, 0, 0, 0, 255)
        SDL_RenderClear(canvas.renderer)
        return True

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

    def stop(self) -> None:
        """Stop recording, destroy every canvas, and reset for later reuse.

        The method is idempotent.  It deliberately retains a finalized movie
        writer so callers can still publish a recording after a window closes.
        """

        self._require_runtime_thread()

        try:
            if self._movie_writer and self._movie_writer.is_recording:
                self._movie_writer.stop_recording()
        finally:
            for canvas in list(self.canvasses.values()):
                self._destroy_canvas_resources(canvas)

            self.canvasses.clear()
            self.listeners.clear()
            self._persistent_textures.clear()
            self.multiple_windows = False
            self._deactivate_runtime()

    def keep(self):
        """Process events until this mainloop's window is closed.

        Reusing the normal dispatcher is important because SDL's event queue
        is process-wide: a close event for an independent mainloop must be
        returned to that loop instead of stopping this one.
        """

        self._require_runtime_thread()
        while self.running:
            if not self._handle_events():
                break
            SDL_Delay(10)

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
        """Create and configure the canvas render target.

        A missing target texture is fatal: allowing construction to continue
        would make later drawing calls silently operate on a null SDL pointer.
        """

        self._require_active_canvas(canvas)
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
        if not texture:
            raise RuntimeError(
                f"Unable to create render texture for canvas {canvas.name!r} "
                f"({x_size}x{y_size}): {self._sdl_error()}"
            )

        try:
            # Alpha blending keeps overlapping persistent drawings composited.
            if SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND) != 0:
                raise RuntimeError(f"Unable to enable texture blending: {self._sdl_error()}")
            if SDL_SetRenderTarget(canvas.renderer, texture) != 0:
                raise RuntimeError(f"Unable to select render texture: {self._sdl_error()}")
            if SDL_SetRenderDrawColor(canvas.renderer, 0, 0, 0, 255) != 0:
                raise RuntimeError(f"Unable to set initial canvas color: {self._sdl_error()}")
            if SDL_RenderClear(canvas.renderer) != 0:
                raise RuntimeError(f"Unable to clear render texture: {self._sdl_error()}")
        except Exception:
            SDL_SetRenderTarget(canvas.renderer, None)
            SDL_DestroyTexture(texture)
            raise

        canvas._persistent_texture = texture

        return texture

    @staticmethod
    def _destroy_canvas_resources(canvas: "CanvasNaive") -> None:
        """Destroy one canvas's SDL resources in dependency order."""

        texture = getattr(canvas, "_persistent_texture", None)
        if texture:
            SDL_DestroyTexture(texture)
            canvas._persistent_texture = None

        renderer = getattr(canvas, "renderer", None)
        if renderer:
            SDL_DestroyRenderer(renderer)
            canvas.renderer = None

        window = getattr(canvas, "window", None)
        if window:
            SDL_DestroyWindow(window)
            canvas.window = None

    def _copy_persistent_texture(self, canvas: "CanvasNaive") -> Optional[ctypes.c_void_p]:
        texture = canvas._persistent_texture

        if not texture:
            return None
        
        SDL_SetRenderTarget(canvas.renderer, None)
        SDL_RenderCopy(canvas.renderer, texture, None, None)

        return texture
