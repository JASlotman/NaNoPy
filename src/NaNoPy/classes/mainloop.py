from sdl2 import SDL_Event

from sdl2 import SDL_Init
from sdl2 import SDL_GetWindowFlags
from sdl2 import SDL_ShowWindow
from sdl2 import SDL_GetRenderer
from sdl2 import SDL_RenderPresent
from sdl2 import SDL_PollEvent
from sdl2 import SDL_SetRenderDrawColor
from sdl2 import SDL_RenderClear
from sdl2 import SDL_Delay
from sdl2 import SDL_DestroyWindow
from sdl2 import SDL_Quit

from sdl2 import SDL_INIT_VIDEO
from sdl2 import SDL_WINDOW_HIDDEN
from sdl2 import SDL_WINDOWEVENT
from sdl2 import SDL_WINDOWEVENT_CLOSE

import ctypes
import platform
import warnings

from NaNoPy.classes.listener import Listener
from NaNoPy.custom_types import WindowType

class Mainloop:    
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO)
        self.event = SDL_Event()
        self.running:bool = True
        self.windows:dict[str, WindowType] = dict()
        self.listeners:dict[str, Listener] = dict()

    def addwindow(self, name:str, window:WindowType) -> None:
        """(deprecated, use add_window() instead.)"""
        warnings.warn(
            "addwindow() is deprecated and will be removed in a future version. "
            "Use add_window() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.add_window(name, window)

    def add_window(self, name, window:WindowType) -> None:
        self.windows[name] = window

    def update(self,name):
        window = self.windows.get(name)
        flags  = SDL_GetWindowFlags(window)
        if (flags & SDL_WINDOW_HIDDEN):
            SDL_ShowWindow(window)
        ren = SDL_GetRenderer(window)
        SDL_RenderPresent(ren)

        while SDL_PollEvent(ctypes.byref(self.event)) != 0:
            if self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_CLOSE:
                self.stop()
            for lstnr in self.listeners:
                self.listeners[lstnr].run(self.event) # type: ignore
       
    def clear(self,name):
        ren = SDL_GetRenderer(self.windows.get(name))
        SDL_SetRenderDrawColor(ren, 0, 0, 0, 255)
        SDL_RenderClear(ren)
        #required for specific linux builds
        if(platform.system() == 'Linux'):
            SDL_RenderPresent(ren) 

    def pause(self,name,time):
        SDL_Delay(time)

    def stop(self):
        self.running = False
        for win in self.windows:
            SDL_DestroyWindow(self.windows[win])
        SDL_Quit()

    def keep(self):
        while self.running:
            while SDL_PollEvent(ctypes.byref(self.event)) != 0:
                if self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_CLOSE:
                    self.stop()

    def add_listener(self, listener:Listener) -> None:
        self.listeners[listener.name] = listener

    def addlistener(self, listener:Listener) -> None:
        """(deprecated, use add_listener() instead)"""
        warnings.warn(
            "addlistener() is deprecated and will be removed in a future version. "
            "Use add_listener() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.add_listener(listener)