import sys
from NaNoPy import Canvas, Writer

try: # Pillow and IPython is only required for notebook embedding
    from IPython.display import clear_output, display
    from PIL import Image
except ImportError:
    pass


def loop(frame_count: int, xSize: int = 300, ySize: int = 300, embedded: bool = True):
    """
    Decorator for running an animation loop in a Jupyter notebook environment.

    This function sets up the rendering environment and returns a decorator
    that handles the frame iteration, screen clearing, and display logic.

    Args:
        frame_count (int): The total number of frames the animation should run for.
        xSize (int, optional): Width of the NaNoPy window. Defaults to 300.
        ySize (int, optional): Height of the NaNoPy window. Defaults to 300.
        embedded: (bool, optional): Should the output be displayed in the cell output. Defaults to True.

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
