import sys
from NaNoPy import Canvas, Writer
from NaNoPy.constants import DEFAULT_CODEC
from typing import Optional

try:  # Pillow and IPython is only required for notebook embedding
    from IPython.display import clear_output, display
    from PIL import Image
except ImportError:
    pass


def loop(
    frame_count: int,
    xSize: int = 300,
    ySize: int = 300,
    embedded: bool = True,
    additive: bool = False,
    record_mp4: Optional[str] = None,
    fps: int = 30,
    codec: str = DEFAULT_CODEC,
):
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
        record_mp4 (str, optional): If provided, records the animation to an MP4 file
                                    at the specified path. Frames are only captured when
                                    this parameter is set (memory-efficient).
                                    Defaults to None (no recording).
        fps (int, optional): Frames per second for the output MP4 video. Defaults to 30.
        codec (str, optional): FFmpeg video encoder. Defaults to lossless H.265.

    Returns:
        Callable: A decorator function that takes the user's rendering function.

    Example:
    ```python
    @loop(frame_count=100, record_mp4="animation.mp4", fps=30)
    def draw_animation(screen: Canvas, pen: Writer, frame_index: int):
        # Drawing logic here. For example:
        pen.draw_circle(xSize // 2, i, 5, color().red, True)
        # Returning False breaks the loop early.
        # Returning a screen.update() displays that frame instead of creating a new one
    ```
    """

    if "ipykernel" not in sys.modules:
        raise EnvironmentError(
            "The 'loop' function decorator is only available in a Jupyter Notebook or IPython environment."
        )

    screen = Canvas("Jupyter_Internal", xSize, ySize)
    pen = Writer(screen)

    # Setup movie recording if requested
    movie_writer = None
    if record_mp4:
        movie_writer = screen.start_recording(record_mp4, fps, codec)

    def decorator(func):
        completed = False
        try:
            for i in range(frame_count):
                if not additive:
                    screen.clear()

                if embedded:
                    clear_output(True)

                frames_before = movie_writer.frame_count() if movie_writer else 0
                im = func(screen, pen, i)

                if embedded:
                    if isinstance(im, Image.Image):
                        display(im)
                        # An image produced by update_embedded() was already
                        # captured; a separately returned image was not.
                        if (
                            movie_writer
                            and movie_writer.is_recording
                            and movie_writer.frame_count() == frames_before
                        ):
                            movie_writer.add_frame(im)
                    else:
                        frame = screen.update_embedded()
                        display(frame)
                        # Frame is automatically captured in update_embedded()
                else:
                    screen.update()
                    if (
                        movie_writer
                        and movie_writer.is_recording
                        and movie_writer.frame_count() == frames_before
                    ):
                        screen.update_embedded()

                if im is False:
                    break

            if movie_writer:
                if movie_writer.is_recording:
                    screen.stop_recording()
                output_path = screen.save_recording()
                print(f"Animation saved to: {output_path}")
            completed = True
        finally:
            if movie_writer and not completed:
                movie_writer.clear()
            screen.NNP.stop()

    return decorator
