import warnings
from typing import Any

from NaNoPy.classes import CanvasNaive, Color, Mainloop, Spline, WriterNaive
from NaNoPy.collisions import apply_to_close_pairs, get_close_pairs

NNP = Mainloop()


class Canvas(CanvasNaive):
    """NaNoPy Canvas object

    canvas(name, x_size, y_size, *, xpos, ypos)
    name: A string that defines the made canvas, each canvas should have a unique name
    x_size: The size in x of the canvas in pixels
    y_size: the size in y of the canvas in pixels
    xpos: the x position of the window (0 is the left)
    ypos: the y position of the window (0 is the top)

    """

    def __init__(
        self,
        name: str,
        x_size: int,
        y_size: int,
        *,
        xpos: int = -1,
        ypos: int = -1,
        driver: int = -1,
    ) -> None:
        super().__init__(name, x_size, y_size, x_pos=xpos, y_pos=ypos, driver=driver, mainloop=NNP)


class Writer(WriterNaive):
    """Object to draw shapes on a nanopy canvas

    writer(canvas)
    canvas: nanopy canvas
    """

    def __init__(self, window: Canvas) -> None:
        super().__init__(window, mainloop=NNP)


class color(Color):
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        warnings.warn(
            "color is deprecated, use Color instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__()


class writer(Writer):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "writer is deprecated, use Writer instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class spline(Spline):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "spline is deprecated, use Spline instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class canvas(Canvas):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "canvas is deprecated, use Canvas instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


__all__ = [
    "NNP",
    "Canvas",
    "Color",
    "Mainloop",
    "Spline",
    "Writer",
    "apply_to_close_pairs",
    "canvas",
    "color",
    "get_close_pairs",
    "spline",
    "writer",
]
