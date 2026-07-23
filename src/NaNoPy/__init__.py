from NaNoPy.classes import Mainloop
from NaNoPy.classes import CanvasNaive
from NaNoPy.classes import Color
from NaNoPy.classes import Spline
from NaNoPy.classes import WriterNaive
from NaNoPy.collisions import get_close_pairs, apply_to_close_pairs

import warnings

# warnings.filterwarnings("ignore", category=DeprecationWarning)

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

    def __init__(
        self,
        name:str,
        xSize:int,
        ySize:int,
        *,
        xpos:int=-1,
        ypos:int=-1,
        driver=-1
    ):
        super().__init__(name, xSize, ySize, x_pos=xpos, y_pos=ypos, driver=driver, NNP=NNP)


class Writer(WriterNaive):
    """Object to draw shapes on a nanopy canvas

    writer(canvas)
    canvas: nanopy canvas
    """

    def __init__(self, window:Canvas):
        super().__init__(window, NNP=NNP)

class color(Color):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "color is deprecated, use Color instead",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__()

class writer(Writer):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "writer is deprecated, use Writer instead",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

class spline(Spline):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "spline is deprecated, use Spline instead",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

class canvas(Canvas):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "canvas is deprecated, use Canvas instead",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

__all__ = [
    "Color", "color",
    "Spline", "spline",
    "Writer", "writer",
    "Canvas", "canvas",
    "Mainloop", "NNP",
    "get_close_pairs", "apply_to_close_pairs"
]
