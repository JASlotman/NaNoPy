from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import math


class canvas:
    def __init__(self,xSize,ySize,*,xpos=-1,ypos=-1):

        if SDL_WasInit(0) == 0:
            SDL_Init(SDL_INIT_VIDEO)
            self.mainWindow = True
        else:
            self.mainWindow = False

        if (xpos < 0 or ypos < 0):
            self.window = SDL_CreateWindow(b"NaNoPy", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, xSize, ySize,
                                           SDL_WINDOW_HIDDEN)
        else:
            self.window = SDL_CreateWindow(b"NaNoPy", xpos, ypos, xSize, ySize, SDL_WINDOW_HIDDEN)

        self.event = SDL_Event()
        self.wasInit = True
        self.running = True

    def update(self):

        if SDL_GetWindowFlags(self.window) == SDL_WINDOW_HIDDEN and not self.wasInit:
            self.running = False
            if self.mainWindow:
                self.stop()
        else:
            SDL_ShowWindow(self.window)
            self.wasInit = False

        ren = SDL_GetRenderer(self.window)
        SDL_RenderPresent(ren)

        while SDL_PollEvent(ctypes.byref(self.event)) != 0:
            if self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_CLOSE:
                w = SDL_GetWindowFromID(self.event.window.windowID)
                SDL_HideWindow(w)

    def clear(self):
        ren = SDL_GetRenderer(self.window)
        SDL_SetRenderDrawColor(ren, 0, 0, 0, 255)
        SDL_RenderClear(ren)

    def pause(self,time):
        SDL_Delay(time)

    def keepWindow(self):
        while self.running:
            while SDL_PollEvent(ctypes.byref(self.event)) != 0:
                if self.event.type == SDL_QUIT:
                    self.running = False
                    break
        SDL_DestroyWindow(self.window)
        SDL_Quit()

    def stop(self):
        SDL_DestroyWindow(self.window)
        SDL_Quit()




class pen:
    def __init__(self,canvas):
        render_flags = (
                SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
        )
        self.renderer = SDL_CreateRenderer(canvas.window, -1, render_flags)
        x = list()
        y = list()
        x.append(0)
        y.append(0)
        xobj = (ctypes.c_int32 * len(x))(*x)
        yobj = (ctypes.c_int32 * len(y))(*y)
        SDL_GetWindowSize(canvas.window,xobj,yobj)
        self.xSize = xobj[0]
        self.ySize = yobj[0]



    def drawPixel(self,x,y,color):
        pixelColor(self.renderer,int(x),int(self.ySize-y),color)

    def drawLine(self,x1,y1,x2,y2,color):
        aalineColor(self.renderer, int(x1), int(self.ySize-y1), int(x2), int(self.ySize-y2), color)

    def drawThickLine(self,x1,y1,x2,y2,w,color):
        thickLineColor(self.renderer, int(x1), int(self.ySize-y1), int(x2), int(self.ySize-y2),int(w), color)

    def drawRectangle(self,x1,y1,w,h,color,filled):
        if filled:
            boxColor(self.renderer,int(x1),int(self.ySize-y1),int(x1+w),int((self.ySize-y1)+h),color)
        else:
            rectangleColor(self.renderer, int(x1), int(y1), int(x1+w),int((self.ySize-y1)+h), color)

    def drawCircle(self,x,y,r,color,filled):
        if filled:
            filledCircleColor(self.renderer,int(x),int(self.ySize-y),int(r),color)
        else:
            aacircleColor(self.renderer,int(x),int(self.ySize-y),int(r),color)

    def drawStar(self,x,y,r,n,color, filled):
        rads = (2*math.pi)/(2*n)
        xs = list()
        ys = list()

        for i in range(n*2):
            rad = r / ( (i % 2) + 1 )
            xs.append(int(x+math.cos(rads*i)*rad))
            ys.append(int((self.ySize)-y+math.sin(rads*i)*rad))

        vx = (ctypes.c_int16 * len(xs))(*xs)
        vy = (ctypes.c_int16 * len(ys))(*ys)

        if filled:
            filledPolygonColor(self.renderer, vx, vy, n*2, color)
        else:
            aapolygonColor(self.renderer,vx,vy,n*2,color)

class color:
    def __init__(self):
        self.red = Color(255,0,0,255)
        self.blue = Color(255, 255, 0, 0)
        self.green = Color(255, 0, 255,0 )
        self.yellow = Color(255, 0, 255, 255)
        self.magenta = Color(255, 255, 0, 255)
        self.cyan = Color(255, 255, 255,0 )
        self.white = Color(255,255,255,255)
        self.gray = Color(255,155,155,155)


    def __call__(self,*,r=255,g=0,b=0):
        return Color(255,b,g,r)
