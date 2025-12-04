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

class Mainloop:    
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO)
        self.event = SDL_Event()
        self.running:bool = True
        self.windowlist:dict[str,object] = dict()
        self.listenerlist:dict[str,object] = dict()

    def addwindow(self, name,window_) -> None:
        self.windowlist[name] = window_

    def update(self,name):
        window = self.windowlist.get(name)
        flags  = SDL_GetWindowFlags(window)
        if (flags & SDL_WINDOW_HIDDEN):
            SDL_ShowWindow(window)
        ren = SDL_GetRenderer(window)
        SDL_RenderPresent(ren)

        while SDL_PollEvent(ctypes.byref(self.event)) != 0:
            if self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_CLOSE:
                self.stop()
            for lstnr in self.listenerlist:
                self.listenerlist[lstnr].run(self.event) # type: ignore
       
    def clear(self,name):
        ren = SDL_GetRenderer(self.windowlist.get(name))
        SDL_SetRenderDrawColor(ren, 0, 0, 0, 255)
        SDL_RenderClear(ren)
        #required for specific linux builds
        if(platform.system() == 'Linux'):
            SDL_RenderPresent(ren) 

    def pause(self,name,time):
        SDL_Delay(time)

    def stop(self):
        self.running = False
        for win in self.windowlist:
            SDL_DestroyWindow(self.windowlist[win])
        SDL_Quit()

    def keep(self):
        while self.running:
            while SDL_PollEvent(ctypes.byref(self.event)) != 0:
                if self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_CLOSE:
                    self.stop()

    def addlistener(self,listener):
        self.listenerlist[listener.name] = listener