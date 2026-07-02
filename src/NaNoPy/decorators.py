import sys
from NaNoPy import Canvas, Writer
from NaNoPy.utils import get_close_pairs
from typing import Iterable, Callable

try: # Pillow and IPython is only required for notebook embedding
    from IPython.display import clear_output, display
    from PIL import Image
except ImportError:
    pass


def loop(frame_count: int, xSize: int = 300, ySize: int = 300, embedded: bool = True, additive: bool = False):
    """
    Decorator for running an animation loop in a Jupyter notebook environment.

    This function sets up the rendering environment and returns a decorator
    that handles the frame iteration, screen clearing, and display logic.

    Args:
        frame_count (int): The total **number of frames** the animation should run for.
        xSize (int, optional): The **width** of the rendering window in pixels. Defaults to 300.
        ySize (int, optional): The **height** of the rendering window in pixels. Defaults to 300.
        embedded (bool, optional): If **True**, the output will be displayed directly 
                                   in the notebook cell output (e.g., for Jupyter/IPython). 
                                   Defaults to True.
        additive (bool, optional): Controls how frames are rendered.
                                   If **True**, new frames are accumulated on top of 
                                   previous frames (additive rendering), meaning the 
                                   screen is not cleared between iterations.
                                   If **False**, the screen is cleared at the start 
                                   of each new frame (non-additive or standard rendering). 
                                   Defaults to False.

    Returns:
        Callable: A decorator function that takes the user's rendering function.

    Example:
    ```python
    @loop(frame_count=100)
    def draw_animation(screen: Canvas, pen: Writer, frame_index: int):
        # Drawing logic here. For example:
        pen.draw_circle(xSize // 2, i, 5, color().red, True)
        # Returning False breaks the loop early.
        # Returning a screen.update() displays that frame instead of creating a new one
    ```
    """

    if not "ipykernel" in sys.modules:
        raise EnvironmentError(
            "The 'loop' function decorator is only available in a Jupyter Notebook or IPython environment."
        )

    screen = Canvas("Jupyter_Internal", xSize, ySize)
    pen = Writer(screen)

    def decorator(func):
        for i in range(frame_count):
            if not additive:
                screen.clear()

            if embedded:
                clear_output(True)

            im = func(screen, pen, i)

            if embedded:
                if isinstance(im, Image.Image):
                    display(im)
                else:
                    display(screen.update_embedded())
            else:
                screen.update()

            if im is False:
                break

        screen.NNP.stop()

    return decorator



def apply_to_close_pairs(
    xs:Iterable[float], ys:Iterable[float], gridsize:int
) -> Callable[[Callable[[int, int], object]], None]:
    """
    Decorator that calls function `func` for all pairs of indices i, j such that
    (xs[i], ys[i]) is close to (xs[j], ys[j]). 
    """
    close_pairs = get_close_pairs(xs, ys, gridsize)

    def decorator(func:Callable[[int, int], object]) -> None:
        for i, j in close_pairs:
            func(i, j)

    return decorator
