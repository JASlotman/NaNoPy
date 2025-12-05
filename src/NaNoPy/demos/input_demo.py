from NaNoPy import *
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDL_KEYUP
from sdl2 import SDL_Event

from NaNoPy.classes import Listener

class LeftRightListener(Listener):
    def __init__(self, name:str):
        super().__init__(name)
        self.dx = 0

    def run(self, event:SDL_Event) -> None:       
        if event.type == SDL_KEYDOWN:
            if event.key.keysym.sym == SDLK_RIGHT:
                self.dx = 3
            elif event.key.keysym.sym == SDLK_LEFT:
                self.dx = -3
        elif event.type == SDL_KEYUP:
            if event.key.keysym.sym in (SDLK_RIGHT,SDLK_LEFT):
                self.dx = 0

xSize = 800
ySize = 600

screen = canvas("Input Demo",xSize,ySize)
p = writer(screen)
screen.add_listener(LeftRightListener("move"))
assert isinstance(screen.listener, LeftRightListener)

w = 50
h = 10
x = xSize/2 - w/2
y = ySize/2 - h/2

while screen.running():
    dx = screen.listener.dx

    x += dx

    p.draw_rectangle(x,y,w,h,Color.white,True)
    screen.update()
    screen.pause(12)
    screen.clear()