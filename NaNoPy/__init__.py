from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import math
import platform
import numpy as np


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
        self.listener = 0
        NNP.addwindow(name, window)
    
    def addlistener(self, listener):
        """Adds a listener object
        
        Listener object should have a name field 
        and a method run(event) that takes the events from the screen
        """
        self.listener = listener
        NNP.addlistener(listener)

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





class writer:
    """Object to draw shapes on a nanopy canvas
    
    writer(canvas)
    canvas: nanopy canvas
    """
    def __init__(self,window,*,driver=-1):
        render_flags = (
                SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
        )
        self.renderer = SDL_CreateRenderer(NNP.windowlist.get(window.name), driver, render_flags)
        x = list()
        y = list()
        x.append(0)
        y.append(0)
        xobj = (ctypes.c_int32 * len(x))(*x)
        yobj = (ctypes.c_int32 * len(y))(*y)
        SDL_GetWindowSize(NNP.windowlist.get(window.name),xobj,yobj)
        self.xSize = xobj[0]
        self.ySize = yobj[0]

        #solves the mac bug essentially adding a clear before initialisation of the writer
        ren = SDL_GetRenderer(NNP.windowlist.get(window.name))
        SDL_SetRenderDrawColor(ren, 0, 0, 0, 255)
        SDL_RenderClear(ren)
        
        #Blitting a clear surface to the renderer before writing something
        surface_old = SDL_GetWindowSurface(NNP.windowlist.get(window.name))
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

    def drawSpline(self,xs,ys,color,loop):
        """Draws spline through list of coordinates xs,ys of given color, loop false gives a line, loop true gives a closed loop
           coordinate information of complete line available in writer.spln object"""
        self.spln = spline(xs,ys,loop)
        for v  in zip(self.spln.splinex,self.spln.spliney):
            self.drawPixel(v[0],v[1],color)

    def drawString(self,x,y,color,text):
        """Draws string on location x,y with given color"""
        gfxPrimitivesSetFont(None, 0, 0)
        stringColor(self.renderer, int(x), int(self.ySize - y), str.encode(text), color)

class color:
    """color object for nanopy shapes
    
    Available colors: red, blue, green, yellow, magenta, cyan, white, gray

    Usage example color().red

    For custom colors use color()(r=<r>,g=<g>,b=<b>,a=<a>) 
    <r>, <g> and <b> are colors between 0 and 255
    <a> is the alpha (opacity) between 0 and 255

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
    
class spline:
    """Spline class for generating a spline trhough given points"""
    def __init__(self,xs,ys,loop):
        self.x = np.array(xs)
        self.y = np.array(ys)            

        n = len(self.x)

        # matrix = np.array(shape=(n,n),dtype = np.float32)
        # resultsy = np.array(shape=(n,1),dtype = np.float32)
        # resultsx = np.array(shape=(n,1),dtype=np.float32)

        self.loop = loop

        if loop:
            segments = self.x.size 
            
            matrix = np.diag(np.full(n-1,1),-1) + np.diag(np.full(n-1,1),+1) + np.diag(np.full(n,4),0)
            matrix[0,n-1] = 1
            matrix[n-1,0] = 1

            

            resultsx = 3 * (np.roll(self.x,-1,0) - np.roll(self.x,1,0))
            resultsy = 3 * (np.roll(self.y,-1,0) - np.roll(self.y,1,0))
        else:

            segments = self.x.size - 1

            matrix = np.diag(np.full(n-1,1),-1) + np.diag(np.full(n-1,1),+1) + np.diag(np.full(n,4),0)
            matrix[0,0] = 2
            matrix[n-1,n-1] = 2

            

            resultsx = 3 * (np.roll(self.x,-1,0) - np.roll(self.x,1,0))
            resultsx[0] = 3* (self.x[1] - self.x[0])
            resultsx[n-1] = 3 * (self.x[n-1]-self.x[n-2])
            resultsy = 3 * (np.roll(self.y,-1,0) - np.roll(self.y,1,0))
            resultsy[0] = 3* (self.y[1] - self.y[0])
            resultsy[n-1] = 3 * (self.y[n-1]-self.y[n-2])

            

        matrix_inv = np.linalg.inv(matrix)
        kx = np.matmul(matrix_inv,resultsx)
        ky = np.matmul(matrix_inv,resultsy)

        

        self.ay = self.y
        self.by = ky
        self.cy = (3 * ((np.roll(self.y,-1,0)-self.y)) - (2*(ky)) - np.roll(ky,-1,0))
        self.dy = (2 * (self.y - np.roll(self.y,-1,0))) + ky + np.roll(ky,-1,0)
        self.ax = self.x
        self.bx = kx
        self.cx = (3 * ((np.roll(self.x,-1,0)-self.x)) - (2*(kx)) - np.roll(kx,-1,0))
        self.dx = (2 * (self.x - np.roll(self.x,-1,0))) + kx + np.roll(kx,-1,0)
        
        

        for i in range(0,segments):       
            samples = max( abs(self.x[i]-self.x[(i+1)%self.x.size]) , abs(self.y[i]-self.y[(i+1)%self.y.size])  )
            samples = math.ceil(samples*20)
            t = np.linspace(0,1,num=samples)
                        
            tempx = (self.ax[i] + self.bx[i]*t + self.cx[i]*(t*t) + self.dx[i]*(t*t*t))
            tempy = (self.ay[i] + self.by[i]*t + self.cy[i]*(t*t) + self.dy[i]*(t*t*t))
            tempdy = (self.by[i] + (2*self.cy[i]*t) + (3*self.dy[i]*(t*t)))
            tempdx = (self.bx[i] + (2*self.cx[i]*t) + (3*self.dx[i]*(t*t)))
            tempdydx = (tempdy/tempdx)

            if i == 0:
                outx = tempx
                outy = tempy
                outdydx = tempdydx
            else:
                outx = np.concatenate((outx,tempx), axis=0)
                outy = np.concatenate((outy,tempy), axis=0)
                outdydx = np.concatenate((outdydx,tempdydx), axis=0)
        
        

        self.splinex = outx
        self.spliney = outy
        self.splinedydx = outdydx

        
                
