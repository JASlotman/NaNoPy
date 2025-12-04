from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import math
import cmath
import platform
import numpy as np

from NaNoPy.classes.mainloop import Mainloop

class WriterNaive:
    """Object to draw shapes on a nanopy canvas
    
    writer(canvas)
    canvas: nanopy canvas
    """
    def __init__(self,window,*,driver=-1,NNP:Mainloop):
        render_flags = (
                SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
        )
        self.renderer = SDL_CreateRenderer(NNP.windows.get(window.name), driver, render_flags)
        x = list()
        y = list()
        x.append(0)
        y.append(0)
        xobj = (ctypes.c_int32 * len(x))(*x)
        yobj = (ctypes.c_int32 * len(y))(*y)
        SDL_GetWindowSize(NNP.windows.get(window.name),xobj,yobj)
        self.xSize = xobj[0]
        self.ySize = yobj[0]

        #solves the mac bug essentially adding a clear before initialisation of the writer
        ren = SDL_GetRenderer(NNP.windows.get(window.name))
        SDL_SetRenderDrawColor(ren, 0, 0, 0, 255)
        SDL_RenderClear(ren)
        
        #Blitting a clear surface to the renderer before writing something
        surface_old = SDL_GetWindowSurface(NNP.windows.get(window.name))
        surface_new = SDL_CreateRGBSurface(0,self.xSize,self.ySize,32,255,0,0,0)
        SDL_BlitSurface(surface_new,None,surface_old,None)





    def drawPixel(self,x,y,color):
        """Draws pixels of given color on x,y coordinate"""
        pixelColor(self.renderer,int(x),int(self.ySize-y),color)

    def drawLine(self,x1,y1,x2,y2,color):
        """Draws line of 1 pixel wide between x1,y1 and x2,y2 of given color"""
        aalineColor(self.renderer, int(x1), int(self.ySize-y1), int(x2), int(self.ySize-y2), color)
        
        #option not using the gfx library
        #     SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_NONE)
        #     SDL_SetRenderDrawColor(self.renderer, color.a,color.b,color.g,color.r)
        #     SDL_RenderDrawLine(self.renderer, int(x1), int(self.ySize-y1), int(x2), int(self.ySize-y2))

    def drawThickLine(self,x1,y1,x2,y2,w,color):
        """Draws line of w pixels wide between x1,y1 and x2,y2 of given color"""
        thickLineColor(self.renderer, int(x1), int(self.ySize-y1), int(x2), int(self.ySize-y2),int(w), color)

    def drawRectangle(self,x1,y1,w,h,color,filled):
        """Draws rectangle with x1,y1 being the top left corner w being the width and h the height and set filled to true to fill it with given color"""
        if filled:
            boxColor(self.renderer,int(x1),int(self.ySize-y1),int(x1+w),int((self.ySize-(y1+h))),color)
        else:
            rectangleColor(self.renderer, int(x1), int(self.ySize-y1), int(x1+w),int((self.ySize-(y1+h))), color)
            

    def drawCircle(self,x,y,r,color,filled):
        """Draws circle with radius r, and x,y being the centre location and set filled to true to fill it with given color"""
        if filled:
            filledCircleColor(self.renderer,int(x),int(self.ySize-y),int(r),color)
        else:
            aacircleColor(self.renderer,int(x),int(self.ySize-y),int(r),color)
                
    def drawStar(self,x,y,r,n,color, filled):
        """Draws star with n points with radius r, and x,y being the centre location and set filled to true to fill it with given color"""
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

    def drawPolygon(self,x,y,r,n,color, filled):
        """Draws n sided polygon with radius r, and x,y being the centre location and set filled to true to fill it with given color"""
        rads = (2*math.pi)/n
        xs = list()
        ys = list()

        for i in range(n):
            xs.append(int(x+math.cos((rads*i)-(math.pi/2))*r))
            ys.append(int((self.ySize)-y+math.sin((rads*i)-(math.pi/2))*r))

        vx = (ctypes.c_int16 * len(xs))(*xs)
        vy = (ctypes.c_int16 * len(ys))(*ys)

        if filled:
            filledPolygonColor(self.renderer, vx, vy, n, color)
        else:
            aapolygonColor(self.renderer,vx,vy,n,color)

    def drawSpline(self,xs,ys,color,loop,filled):
        """Draws spline through list of coordinates xs,ys of given color, loop false gives a line, loop true gives a closed loop
           coordinate information of complete line available in writer.spln object"""
        self.spln = spline(xs,ys,loop)
        for v  in zip(self.spln.splinex,self.spln.spliney):
            self.drawPixel(v[0],v[1],color)
        if loop and filled:
            for v in zip(self.spln.insidex,self.spln.insidey):
                self.drawPixel(v[0],v[1],color)

    def drawString(self,x,y,color,text):
        """Draws string on location x,y with given color"""
        gfxPrimitivesSetFont(None, 0, 0)
        stringColor(self.renderer, int(x), int(self.ySize - y), str.encode(text), color)