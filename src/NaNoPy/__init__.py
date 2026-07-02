from NaNoPy.classes import Mainloop
from NaNoPy.classes import CanvasNaive
from NaNoPy.classes import Color
from NaNoPy.classes import Spline
from NaNoPy.classes import WriterNaive
from NaNoPy.collisions import get_close_pairs, apply_to_close_pairs


import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

NNP = Mainloop()


class Canvas(CanvasNaive):
    """NaNoPy Canvas object

    canvas(name,xSize,ySize,*,xpos,ypos)
    name: A string that defines the made canvas, each canvas should have a unique name
    xSize: The size in x of the canvas in pixels
    ySize: the size in y of the canvas in pixels
    xpos: the x position of the window (0 is the left)
    ypos: the y position of the window (0 is the top)

    """

    def __init__(self, name, xSize, ySize, *, xpos=-1, ypos=-1, driver=-1):
        super().__init__(name, xSize, ySize, x_pos=xpos, y_pos=ypos, driver=driver, NNP=NNP)


class Writer(WriterNaive):
    """Object to draw shapes on a nanopy canvas

    writer(canvas)
    canvas: nanopy canvas
    """

    def __init__(self, window):
        super().__init__(window, NNP=NNP)


# Defining aliases
color = Color
spline = Spline
writer = Writer
canvas = Canvas
