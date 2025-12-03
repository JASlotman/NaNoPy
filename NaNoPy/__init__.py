from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import math
import cmath
import platform
import numpy as np
import sys

IS_JUPYTER = 'ipykernel' in sys.modules

if IS_JUPYTER:
    import tempfile
    from PIL import Image
    from IPython.display import clear_output, display

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
        ren = SDL_GetRenderer(window)

        while SDL_PollEvent(ctypes.byref(self.event)) != 0:
                if self.event.type == SDL_WINDOWEVENT and self.event.window.event == SDL_WINDOWEVENT_CLOSE:
                    self.stop()
                for lstnr in self.listenerlist:
                    self.listenerlist[lstnr].run(self.event)

        if IS_JUPYTER:
            #dynamically get screen size as it may change per cell
            xSize = ctypes.c_int()
            ySize = ctypes.c_int()

            SDL_GetWindowSize(window, ctypes.byref(xSize), ctypes.byref(ySize))

            argb_mask = [0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000]

            surface = SDL_CreateRGBSurface(0,xSize.value, ySize.value, 32, *argb_mask) #create empty surface

            #render screen to surface
            SDL_RenderReadPixels(ren, None, SDL_PIXELFORMAT_ARGB8888,
                surface.contents.pixels, surface.contents.pitch)
            
            try:
                with tempfile.NamedTemporaryFile() as tmp:
                    save_bmp(surface, tmp.name, True)

                    img = Image.open(tmp.name)
                    SDL_FreeSurface(surface) #free memory
                    return img
            except Exception as e:
                SDL_FreeSurface(surface) #free memory
                print(f"Failed to save frame: {e}")

        else:
            flags  = SDL_GetWindowFlags(window)
            if (flags & SDL_WINDOW_HIDDEN):
                SDL_ShowWindow(window)

            SDL_RenderPresent(ren)
       

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
        return NNP.update(self.name)

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
            samples = math.ceil(samples*2.5)
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

        if loop:
            self.getInsidePix()

    def getInsidePix(self):
        inds = self.spliney.argsort()
        sortedy = self.spliney[inds]
        sortedx = self.splinex[inds]
        boundingbox = [np.min(self.splinex),np.min(self.spliney),np.max(self.splinex),np.max(self.spliney)]
        sortedy = sortedy - boundingbox[1]
        sortedx = sortedx - boundingbox[0]
        minx = np.full(math.ceil(boundingbox[3]-boundingbox[1])+1,math.ceil(boundingbox[2]-boundingbox[0])+1)
        maxx = np.zeros(math.ceil(boundingbox[3]-boundingbox[1])+1)

        for j in range(len(sortedy)):
            i = math.ceil(sortedy[j])
            if sortedx[j] < minx[i]:
                minx[i] = sortedx[j]
            if sortedx[j] > maxx[i]:
                maxx[i] = sortedx[j]
            
             

        for i in range(len(minx)):
            if i == 0:
                self.insidex = (np.arange(math.floor(minx[i]),math.ceil(maxx[i]))+boundingbox[0])
                self.insidey = (np.full(math.ceil(maxx[i])-math.floor(minx[i]),(i+boundingbox[1])))                
                
            else:
                self.insidex = np.concatenate((self.insidex,(np.arange(math.floor(minx[i]),math.ceil(maxx[i]))+boundingbox[0])),axis=0)
                self.insidey = np.concatenate((self.insidey,(np.full(math.ceil(maxx[i])-math.floor(minx[i]),(i+boundingbox[1])))),axis=0)

    def getInside(self,x,y):

        


        splncx = np.average(self.ax)
        splncy = np.average(self.ay)
        

        #draw line trhough given point and center, extend beyond bounding box

        if splncx < x:
            x1 = splncx
            x2 = x
            y1 = splncy
            y2 = y
        if splncx >= x:
            x1 = x
            x2 = splncx
            y1 = y
            y2 = splncy
        
        dx = x2-x1
        dy = y2-y1

        if dx == 0 and dy == 0:
            return True
        
        
        numberofsegments = len(self.ax)
            
        if self.loop:
            n = numberofsegments
        else:
            n = numberofsegments-1
        
        valid_intercepts = []
        all_intercepts = []

        for segno in range(n):
            if dx != 0: 
                
                E = dy/dx
                F = y1 - (x1*E)

                a = self.ax[segno] 
                b = self.bx[segno] 
                c = self.cx[segno]
                d = self.dx[segno]
                e = self.ay[segno]
                f = self.by[segno]
                g = self.cy[segno]
                h = self.dy[segno]
                i = E
                j = F

                #redefine an a+bx+cx2+dx2 formula

                a = ((i*a)+j)-e
                b = (i*b)-f
                c = (i*c)-g
                d = (i*d)-h

            if dx == 0:
                a = self.ax[segno] - x1
                b = self.bx[segno] 
                c = self.cx[segno]
                d = self.dx[segno] 

                    
            #solve cubic for real values 
            #https://medium.com/@mephisto_Dev/solving-cubic-equation-using-cardanos-method-with-python-9465f0b92277
            #https://math.stackexchange.com/questions/243961/find-x-given-y-in-a-cubic-function

            p = (3*d*b - c**2) / (3*d**2)
            q = (2*c**3 - 9*d*c*b + 27*d**2*a) / (27*d**3)
            delta = (q**2 / 4 + p**3 / 27)

            # determine number and type of roots
            if delta > 0:  # one real and two complex roots
                    
                u = (-q/2 + cmath.sqrt(delta))
                v = (-q/2 - cmath.sqrt(delta))

                u_regular = u ** (1./3) if u >= 0 else -(-u)**(1./3)
                u_cbrt = math.cbrt(u) 
                v_regular = v ** (1./3) if v >= 0 else -(-v)**(1./3)
                v_cbrt = math.cbrt(v) 

                xx1 = u_regular + v - c / (3*d)
                xx2 = -(u_regular + v_regular)/2 - c / (3*d) + (u_regular - v_regular)*cmath.sqrt(3)/2j
                xx3 = -(u_regular + v_regular)/2 - c / (3*d) - (u_regular - v_regular)*cmath.sqrt(3)/2j
                xx4 = u_cbrt + v_cbrt - c / (3*d)
                xx5 = -(u_cbrt + v_cbrt)/2 - c / (3*d) + (u_cbrt - v_cbrt)*cmath.sqrt(3)/2j
                xx6 = -(u_cbrt + v_cbrt)/2 - c / (3*d) - (u_cbrt - v_cbrt)*cmath.sqrt(3)/2j
                # print("One real root and two complex roots:")
                # print("x1 = ", xx1.real)
                # print("x2 = ", xx2)
                # print("x3 = ", xx3)
            elif delta == 0:  # three real roots, two are equal
                u = (-q/2)
                u_regular = u ** (1./3) if u >= 0 else -(-u)**(1./3)
                u_cbrt = math.cbrt(u) 
                xx1 = ((2*u_regular) - c) / (3*d)
                xx2 = ((-u_regular) - c) / (3*d)
                xx3 = ((-u_regular) - c) / (3*d)
                xx4 = ((2*u_cbrt) - c) / (3*d)
                xx5 = ((-u_cbrt) - c) / (3*d)
                xx6 = ((-u_cbrt) - c) / (3*d)
                # print("Three real roots, two are equal:")
                # print("x1 = ", xx1.real)
                # print("x2 = ", xx2.real)
                # print("x3 = ", xx3.real)
            else:  # three distinct real roots
                u = (-q/2 + cmath.sqrt(delta))
                v = (-q/2 - cmath.sqrt(delta))
                u_regular = u ** (1./3) if u >= 0 else -(-u)**(1./3)
                u_cbrt = math.cbrt(u) 
                v_regular = v ** (1./3) if v >= 0 else -(-v)**(1./3)
                v_cbrt = math.cbrt(v) 

                xx1 = u_regular + v - c / (3*d)
                xx2 = -(u_regular + v_regular)/2 - c / (3*d) + (u_regular - v_regular)*cmath.sqrt(3)/2j
                xx3 = -(u_regular + v_regular)/2 - c / (3*d) - (u_regular - v_regular)*cmath.sqrt(3)/2j
                xx4 = u_cbrt + v_cbrt - c / (3*d)
                xx5 = -(u_cbrt + v_cbrt)/2 - c / (3*d) + (u_cbrt - v_cbrt)*cmath.sqrt(3)/2j
                xx6 = -(u_cbrt + v_cbrt)/2 - c / (3*d) - (u_cbrt - v_cbrt)*cmath.sqrt(3)/2j
                # print("Three distinct real roots:")
                # print("x1 = ", xx1.real)
                # print("x2 = ", xx2.real)
                # print("x3 = ", xx3.real)

            if delta > 0:
                all_intercepts.append([segno,xx1.real])
                if 0 <= xx1.real <= 1:
                    tint = xx1.real
                    valid_intercepts.append([segno,tint])
                all_intercepts.append([segno,xx4.real])
                if 0 <= xx4.real <= 1:
                    tint = xx4.real
                    valid_intercepts.append([segno,tint])
            if delta <= 0:
                all_intercepts.append([segno,xx1.real])
                all_intercepts.append([segno,xx2.real])
                all_intercepts.append([segno,xx3.real])
                if 0 <= xx1.real <= 1:
                    tint = xx1.real
                    valid_intercepts.append([segno,tint])
                if 0 <= xx2.real <= 1:
                    tint = xx2.real
                    valid_intercepts.append([segno,tint])
                if 0 <= xx3.real <= 1:
                    tint = xx3.real
                    valid_intercepts.append([segno,tint])
                all_intercepts.append([segno,xx4.real])
                all_intercepts.append([segno,xx5.real])
                all_intercepts.append([segno,xx6.real])
                if 0 <= xx4.real <= 1:
                    tint = xx4.real
                    valid_intercepts.append([segno,tint])
                if 0 <= xx5.real <= 1:
                    tint = xx5.real
                    valid_intercepts.append([segno,tint])
                if 0 <= xx6.real <= 1:
                    tint = xx6.real
                    valid_intercepts.append([segno,tint])
        
        countbefore = 0

        

        truevalids = []

        for i in range(len(valid_intercepts)):
            segmentno = valid_intercepts[i][0]
            tintercept = valid_intercepts[i][1]

            xint = self.ax[segmentno]+(self.bx[segmentno]*tintercept)+(self.cx[segmentno]*(tintercept**2))+(self.dx[segmentno]*(tintercept**3))
            yint = self.ay[segmentno]+(self.by[segmentno]*tintercept)+(self.cy[segmentno]*(tintercept**2))+(self.dy[segmentno]*(tintercept**3))
            valid_intercepts[i].append(xint)
            valid_intercepts[i].append(yint)

            if  math.isclose(yint , (E*xint) + F):

                truevalids.append([valid_intercepts[i],xint,yint])

                if xint < x:
                    countbefore += 1
        
        

        if countbefore%2 == 1:
            return True
        else:
            return False

def loop(frame_count: int, xSize: int = 300, ySize: int = 300):
    """
    Decorator for running an animation loop in a Jupyter notebook environment.

    This function sets up the rendering environment and returns a decorator 
    that handles the frame iteration, screen clearing, and display logic.

    Args:
        frame_count (int): The total number of frames the animation should run for.
        xSize (int, optional): Width of the NaNoPy window. Defaults to 300.
        ySize (int, optional): Height of the NaNoPy window. Defaults to 300.

    Returns:
        Callable: A decorator function that takes the user's rendering function.
        
    Example:
    ```python
    @loop(frame_count=100)
    def draw_animation(screen: canvas, pen: writer, frame_index: int):
        # Drawing logic here. For example:
        pen.drawCircle(xSize // 2, i, 5, color().red, True)
        # Returning False breaks the loop early.
        # Returning a screen.update() displays that frame instead of creating a new one
    ```
    """

    if not IS_JUPYTER:
        raise EnvironmentError("The 'loop' function decorator is only available in a Jupyter Notebook or IPython environment.")

    screen = canvas("Jupyter_Internal", xSize, ySize) 
    pen = writer(screen)

    def decorator(func):
        for i in range(frame_count):
        
            screen.clear()
            clear_output(True)

            im = func(screen, pen, i)

            if isinstance(im, Image.Image): display(im)
            else: display(screen.update())

            if im == False: break

        NNP.stop()
    
    return decorator