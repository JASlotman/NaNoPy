from NaNoPy import *
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDL_KEYUP

class inputlistener:

    def __init__(self,name):
        self.name = name
        self.dx = 0
        
    def run(self,event):       
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
screen.addlistener(inputlistener("move"))

w = 50
h = 10
x = xSize/2 - w/2
y = ySize/2 - h/2

while screen.running():

    dx = screen.listener.dx

    x += dx

    p.drawRectangle(x,y,w,h,color().white,True)
    screen.update()
    screen.pause(12)
    screen.clear()