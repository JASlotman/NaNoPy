from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import math


class Mainloop:    
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO)
        self.event = SDL_Event()
        self.running = True
        self.windowlist = dict()
        self.listenerlist = dict()


    def addwindow(self,name,window_):
        self.windowlist[name] = window_

    def update(self,name):
        window = self.windowlist.get(name)
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
        #SDL_RenderPresent(ren)

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



NNP = Mainloop()

class canvas:
    """NaNoPy Canvas object
    
    canvas(name,xSize,ySize,*,xpos,ypos)
    name: A string that defines the made canvas, each canvas should have a unique name
    xSize: The size in x of the canvas in pixels
    ySize: the size in y of the canvas in pixels
    xpos: the x position of the window (0 is the left)
    ypos: the y position of the window (0 is the top)

    """
    def __init__(self,name,xSize,ySize,*,xpos=-1,ypos=-1):

        if (xpos < 0 or ypos < 0):
            window = SDL_CreateWindow(str.encode(name), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, xSize, ySize,SDL_WINDOW_HIDDEN)
        else:
            window = SDL_CreateWindow(str.encode(name), xpos, ypos, xSize, ySize, SDL_WINDOW_HIDDEN)

        self.name = name
        NNP.addwindow(name, window)


    def update(self):
        """Update the canvas"""
        NNP.update(self.name)

    def clear(self):
        """Clear the canvas """
        NNP.clear(self.name)

    def pause(self,time):
        """Pause the canvas for a time in ms"""
        NNP.pause(self.name,time)

    def keepwindow(self):
        """Keep window on screen if not running any code (for showing a single screen) or finite number of frames"""
        NNP.keep()

    def running(self):
        """method returning if a process is running in the canvas, returns false if window is closed"""
        return NNP.running





class pen:
    """Object to draw shapes on a nanopy canvas
    
    pen(canvas)
    canvas: nanopy canvas
    """
    def __init__(self,window):
        render_flags = (
                SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
        )
        self.renderer = SDL_CreateRenderer(NNP.windowlist.get(window.name), -1, render_flags)
        x = list()
        y = list()
        x.append(0)
        y.append(0)
        xobj = (ctypes.c_int32 * len(x))(*x)
        yobj = (ctypes.c_int32 * len(y))(*y)
        SDL_GetWindowSize(NNP.windowlist.get(window.name),xobj,yobj)
        self.xSize = xobj[0]
        self.ySize = yobj[0]



    def drawPixel(self,x,y,color):
        pixelColor(self.renderer,int(x),int(self.ySize-y),color)

    def drawLine(self,x1,y1,x2,y2,color):
        
        aalineColor(self.renderer, int(x1), int(self.ySize-y1), int(x2), int(self.ySize-y2), color)
        
        #option not using the gfx library
        #     SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_NONE)
        #     SDL_SetRenderDrawColor(self.renderer, color.a,color.b,color.g,color.r)
        #     SDL_RenderDrawLine(self.renderer, int(x1), int(self.ySize-y1), int(x2), int(self.ySize-y2))

    def drawThickLine(self,x1,y1,x2,y2,w,color):
        thickLineColor(self.renderer, int(x1), int(self.ySize-y1), int(x2), int(self.ySize-y2),int(w), color)

    def drawRectangle(self,x1,y1,w,h,color,filled):
        if filled:
            boxColor(self.renderer,int(x1),int(self.ySize-y1),int(x1+w),int((self.ySize-(y1+h))),color)
        else:
            rectangleColor(self.renderer, int(x1), int(self.ySize-y1), int(x1+w),int((self.ySize-(y1+h))), color)
            

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

    def drawString(self,x,y,color,text):
        gfxPrimitivesSetFont(None, 0, 0)
        stringColor(self.renderer, int(x), int(self.ySize - y), str.encode(text), color)

class color:
    """color object for nanopy shapes
    
    Available colors: red, blue, green, yellow, magenta, cyan, white, gray

    Usage example color().red

    For custom colors use color()(r,g,b,a) 
    r, g and b are colors between 0 and 255
    a is the alpha (opacity) between 0 and 255

    """

    def __init__(self):
        self.red = Color(255,0,0,255)
        self.blue = Color(255, 255, 0, 0)
        self.green = Color(255, 0, 255,0 )
        self.yellow = Color(255, 0, 255, 255)
        self.magenta = Color(255, 255, 0, 255)
        self.cyan = Color(255, 255, 255,0 )
        self.white = Color(255,255,255,255)
        self.gray = Color(255,155,155,155)


    def __call__(self,*,r=255,g=0,b=0,a=255):
        return Color(a,b,g,r)

class listener:
    def __init__(self, listener):
        self.lstnr = listener
        NNP.addlistener(listener)
