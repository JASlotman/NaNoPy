from sdl2 import SDL_CreateWindow
from sdl2 import SDL_WINDOWPOS_CENTERED
from sdl2 import SDL_WINDOW_HIDDEN
from NaNoPy.classes.mainloop import Mainloop

from NaNoPy.custom_types import WindowType
from NaNoPy.classes.listener import Listener

class CanvasNaive:
    """NaNoPy Canvas object
    
    canvas(name,xSize,ySize,*,xpos,ypos)
    name: A string that defines the made canvas, each canvas should have a unique name
    xSize: The size in x of the canvas in pixels
    ySize: the size in y of the canvas in pixels
    xpos: the x position of the window (0 is the left)
    ypos: the y position of the window (0 is the top)

    """
    def __init__(
            self,
            name:str,
            xSize:int,
            ySize:int,
            *,
            xpos:int=-1,
            ypos:int=-1,
            NNP:Mainloop
            ):

        if xpos < 0 or ypos < 0:
            xpos = SDL_WINDOWPOS_CENTERED
            ypos = SDL_WINDOWPOS_CENTERED

        window:WindowType = SDL_CreateWindow(
            str.encode(name), 
            xpos, ypos, 
            xSize, ySize, 
            SDL_WINDOW_HIDDEN
            )
        
        self.name = name
        self.listener:None|Listener = None
        self.NNP = NNP
        self.NNP.addwindow(name, window)
    
    def addlistener(self, listener:Listener):
        """Adds a listener object
        
        Listener object should have a name field 
        and a method run(event) that takes the events from the screen
        """
        self.listener = listener
        self.NNP.addlistener(listener)

    def update(self):
        """Update the canvas"""
        self.NNP.update(self.name)

    def clear(self):
        """Clear the canvas """
        self.NNP.clear(self.name)

    def pause(self,time):
        """Pause the canvas for a time in ms"""
        self.NNP.pause(self.name,time)

    def keepwindow(self):
        """Keep window on screen if not running any code (for showing a single screen) or finite number of frames"""
        self.NNP.keep()

    def running(self):
        """method returning if a process is running in the canvas, returns false if window is closed"""
        return self.NNP.running