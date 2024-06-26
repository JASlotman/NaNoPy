from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import math


class canvas:
    def __init__(self,xSize,ySize):

        SDL_Init(SDL_INIT_VIDEO)
        self.window = SDL_CreateWindow(b"NaNoPy", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, xSize, ySize, SDL_WINDOW_HIDDEN)

    def update(self):
        SDL_ShowWindow(self.window)
        ren = SDL_GetRenderer(self.window)
        SDL_RenderPresent(ren)


        self.event = SDL_Event()
        running = True
        while running:
            while SDL_PollEvent(ctypes.byref(self.event)) != 0:
                if self.event.type == SDL_QUIT:
                    running = False
                    break
        SDL_DestroyWindow(self.window)
        SDL_Quit()

    def clear(self):
        ren = SDL_GetRenderer(self.window)
        SDL_SetRenderDrawColor(ren, 0, 0, 0, 255)
        SDL_RenderClear(ren)

    def pause(time):
        SDL_Delay(time)

class pen:
    def __init__(self,canvas):
        render_flags = (
                SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
        )
        self.renderer = SDL_CreateRenderer(canvas.window, -1, render_flags)


    def drawPixel(self,x,y,color):
        pixelColor(self.renderer,int(x),int(y),color)

    def drawLine(self,x1,y1,x2,y2,color):
        aalineColor(self.renderer, int(x1), int(y1), int(x2), int(y2), color)

    def drawThickLine(self,x1,y1,x2,y2,w,color):
        thickLineColor(self.renderer, int(x1), int(y1), int(x2), int(y2),int(w), color)

    def drawRectangle(self,x1,y1,w,h,color,filled):
        if filled:
            boxColor(self.renderer,int(x1),int(y1),int(x1+w),int(y1+h),color)
        else:
            rectangleColor(self.renderer, int(x1), int(y1), int(x1+w),int(y1+h), color)

    def drawCircle(self,x,y,r,color,filled):
        if filled:
            filledCircleColor(self.renderer,int(x),int(y),int(r),color)
        else:
            aacircleColor(self.renderer,int(x),int(y),int(r),color)

    def drawStar(self,x,y,r,n,color, filled):
        rads = (2*math.pi)/(2*n)
        xs = list()
        ys = list()

        for i in range(n*2):
            rad = r / ( (i % 2) + 1 )
            xs.append(int(x+math.cos(rads*i)*rad))
            ys.append(int(y+math.sin(rads*i)*rad))

        vx = (ctypes.c_int16 * len(xs))(*xs)
        vy = (ctypes.c_int16 * len(ys))(*ys)

        if filled:
            filledPolygonColor(self.renderer, vx, vy, n*2, color)
        else:
            aapolygonColor(self.renderer,vx,vy,n*2,color)

class color:
    def __init__(self,*,r=0,g=0,b=0):
        self.red = Color(255,0,0,255)
        self.blue = Color(255, 255, 0, 0)
        self.green = Color(255, 0, 255,0 )
        self.yellow = Color(255, 0, 255, 255)
        self.magenta = Color(255, 255, 0, 255)
        self.cyan = Color(255, 255, 255,0 )
        self.white = Color(255,255,255,255)
        self.gray = Color(255,155,155,155)
        self.r=r
        self.g=g
        self.b=b

    def __call__(self):
        return Color(255,self.b,self.g,self.r)
