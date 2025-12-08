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

import ctypes
import warnings
import tempfile
from typing import Optional, Any

from NaNoPy.classes.listener import Listener
from NaNoPy.constants import ARGB_MASK
from NaNoPy.custom_types import WindowType

try:  # Pillow is only required for notebook embedding
    from PIL import Image
except ImportError:
    pass


class Mainloop:
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO)
        self.event = SDL_Event()
        self.running: bool = True
        self.windows: dict[str, WindowType] = {}
        self.listeners: dict[str, Listener] = {}
        self._persistent_textures: dict[str, ctypes.c_void_p] = {}

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

    def update(self, name: str):
        window, ren = self.get_window_and_renderer(name)

        flags = SDL_GetWindowFlags(window)
        if (flags & SDL_WINDOW_HIDDEN):
            SDL_ShowWindow(window)

        texture = self._copy_persistent_texture(name, ren)
        SDL_RenderPresent(ren)
        if texture:
            SDL_SetRenderTarget(ren, texture)

        self._handle_events()

    def update_embedded(self, name) -> Image:
        if Image is None:
            raise RuntimeError("Embedded rendering requires Pillow to be installed")

        window, ren = self.get_window_and_renderer(name)

        self._handle_events()

        x_size = ctypes.c_int()
        y_size = ctypes.c_int()

        SDL_GetWindowSize(window, ctypes.byref(x_size), ctypes.byref(y_size))

        # Create empty surface
        surface = SDL_CreateRGBSurface(0, x_size.value, y_size.value, 32, *ARGB_MASK)

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
            return Image.new("1", (x_size.value, y_size.value))
        

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

        for tex in self._persistent_textures.values():
            SDL_DestroyTexture(tex)

        self._persistent_textures.clear()

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

    def ensure_persistent_texture(self, name: str, renderer, width: int, height: int):
        texture = self._persistent_textures.get(name)

        # If texture exist already return
        if texture:
            return texture

        texture = SDL_CreateTexture(
            renderer,
            SDL_PIXELFORMAT_RGBA8888,
            SDL_TEXTUREACCESS_TARGET,
            width,
            height,
        )

        # Set blending mode to alpha blending
        # This ensures overlapping textures render correctly
        SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND)
    
        self._persistent_textures[name] = texture

        return texture

    def _copy_persistent_texture(self, name: str, renderer) -> Optional[ctypes.c_void_p]:
        texture = self._persistent_textures.get(name)

        if not texture:
            return None
        
        SDL_SetRenderTarget(renderer, None)
        SDL_RenderCopy(renderer, texture, None, None)

        return texture
