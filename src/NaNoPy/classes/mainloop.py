from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import math
import cmath
import platform
import numpy as np

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
                self.listenerlist[lstnr].run(self.event)
       
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