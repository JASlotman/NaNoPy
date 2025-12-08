from sdl2 import SDL_Event

from sdl2 import SDL_Init
from sdl2 import SDL_GetWindowFlags
from sdl2 import SDL_GetWindowSize
from sdl2 import SDL_CreateRGBSurface
from sdl2 import SDL_FreeSurface
from sdl2 import SDL_RenderReadPixels
from sdl2 import SDL_ShowWindow
from sdl2 import SDL_GetRenderer
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
from sdl2 import SDL_PIXELFORMAT_RGBA8888
from sdl2 import SDL_TEXTUREACCESS_TARGET
from sdl2 import SDL_SetTextureBlendMode
from sdl2 import SDL_BLENDMODE_BLEND

from sdl2 import SDL_INIT_VIDEO
from sdl2 import SDL_WINDOW_HIDDEN
from sdl2 import SDL_WINDOWEVENT
from sdl2 import SDL_WINDOWEVENT_CLOSE
from sdl2 import SDL_PIXELFORMAT_ARGB8888

from sdl2.ext import save_bmp
from sdl2.sdlgfx import gfxPrimitivesSetFont

import ctypes
import warnings
import tempfile
from typing import Optional, TYPE_CHECKING

from NaNoPy.classes.listener import Listener
from NaNoPy.constants import ARGB_MASK
from NaNoPy.custom_types import WindowType

from PIL import Image

if TYPE_CHECKING:
    from NaNoPy.classes.canvas import CanvasNaive


class Mainloop:
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO)
        self.event = SDL_Event()
        self.running: bool = True
        self.windows: dict[str, WindowType] = {} # Not used
        self.canvasses: dict[str, CanvasNaive] = {}
        self.listeners: dict[str, Listener] = {}

        self.multiple_windows = False

    def addwindow(self, name: str, window: WindowType) -> None:
        """(deprecated, use add_window() instead.)"""
        warnings.warn(
            "addwindow() is deprecated and will be removed in a future version. "
            "Use add_window() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_window(name, window)

    def add_window(self, name, window: WindowType) -> None:
        self.windows[name] = window

    def add_canvas(self, canvas: CanvasNaive):
        self.canvasses[canvas.name] = canvas

        # Don't check it during runtime to reduce accession
        if len(self.canvasses) > 1:
            self.multiple_windows = True

    def update(self, canvas: CanvasNaive):
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

    def update_embedded(self, canvas: CanvasNaive) -> Image.Image:
        if Image is None:
            raise RuntimeError("Embedded rendering requires Pillow to be installed")

        ren = canvas.renderer

        if self.multiple_windows and canvas._reload_fonts:
            gfxPrimitivesSetFont(None, 0, 0)
            canvas._reload_fonts = False

        self._handle_events()

        x_size, y_size = canvas.get_window_size()

        # Create empty surface
        surface = SDL_CreateRGBSurface(0, x_size, y_size, 32, *ARGB_MASK)

        # Render screen to surface
        SDL_RenderReadPixels(
            ren,
            None,
            SDL_PIXELFORMAT_ARGB8888,
            surface.contents.pixels,
            surface.contents.pitch,
        )
        
        surface_freed = False

        try:
            with tempfile.NamedTemporaryFile() as tmp:
                save_bmp(surface, tmp.name, True)

                img = Image.open(tmp.name)
                SDL_FreeSurface(surface)  # Free memory
                return img
   
        except Exception as e:
            print(f"Failed to save frame: {e}")

            if not surface_freed:         # Free memory
                SDL_FreeSurface(surface)

            # Return black image on error
            return Image.new("1", (x_size, y_size))
        

    def get_window_and_renderer(self, name: str):
        window = self.windows.get(name)
        ren = SDL_GetRenderer(window)

        return window, ren

    def _handle_events(self):
        while SDL_PollEvent(ctypes.byref(self.event)) != 0:
            if (self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_CLOSE):
                self.stop()

            for listener in self.listeners.values():
                listener.run(self.event) 

    def clear(self, name):
        _, ren = self.get_window_and_renderer(name)

        SDL_SetRenderDrawColor(ren, 0, 0, 0, 255)
        SDL_RenderClear(ren)

    def pause(self, time):
        SDL_Delay(time)

    def stop(self):
        self.running = False

        for canvas in self.canvasses.values():
            SDL_DestroyTexture(canvas._persistent_texture)

        for win in self.windows.values():
            SDL_DestroyWindow(win)

        SDL_Quit()

    def keep(self):
        while self.running:
            while SDL_PollEvent(ctypes.byref(self.event)) != 0:
                if (
                    self.event.type == SDL_WINDOWEVENT
                    and self.event.window.event == SDL_WINDOWEVENT_CLOSE
                ):
                    self.stop()

    def add_listener(self, listener: Listener) -> None:
        self.listeners[listener.name] = listener

    def addlistener(self, listener: Listener) -> None:
        """(deprecated, use add_listener() instead)"""
        warnings.warn(
            "addlistener() is deprecated and will be removed in a future version. "
            "Use add_listener() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_listener(listener)

    def ensure_persistent_texture(self, canvas: CanvasNaive):
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

        return texture

    def _copy_persistent_texture(self, canvas: CanvasNaive) -> Optional[ctypes.c_void_p]:
        texture = canvas._persistent_texture

        if not texture:
            return None
        
        SDL_SetRenderTarget(canvas.renderer, None)
        SDL_RenderCopy(canvas.renderer, texture, None, None)

        return texture
