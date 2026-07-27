"""MP4 Export Examples for NaNoPy

This file demonstrates how to export animations as MP4 videos in both
Jupyter notebook and non-Jupyter (standard Python) modes.

Run ``nanopy --list`` to see the examples as ``mp4_bouncing_ball``,
``mp4_rotating_square``, ``mp4_advanced_recording`` and ``mp4_with_audio``, then
run one with e.g. ``nanopy mp4_bouncing_ball``. This file also has its own
command-line interface: ``python -m NaNoPy.demos.mp4_export_examples --help``
lists the examples as subcommands.

The same examples can be imported and called from your own code::

    from NaNoPy.demos import mp4_bouncing_ball

    help(mp4_bouncing_ball)
    mp4_bouncing_ball()

Requirements:
    - ffmpeg must be installed on your system
    - Ubuntu/Debian: sudo apt-get install ffmpeg
    - macOS: brew install ffmpeg
    - Windows: Download from ffmpeg.org or: choco install ffmpeg
"""

# ============================================================================
# JUPYTER NOTEBOOK EXAMPLE
# ============================================================================
# For Jupyter/IPython notebooks, use the @loop decorator with record_mp4 param
#
# Example:
#
#   from NaNoPy.decorators import loop
#   from NaNoPy import Canvas, Writer, Color
#   import math
#   from pathlib import Path
#
#   output_dir = Path.cwd() / "nanopy-output"
#   output_dir.mkdir(parents=True, exist_ok=True)
#
#   @loop(
#       frame_count=120,
#       xSize=400,
#       ySize=400,
#       record_mp4=str(output_dir / "my_animation.mp4"),
#       fps=30,
#   )
#   def animated_circle(screen: Canvas, pen: Writer, i: int):
#       x = 200 + 100 * math.sin(i * 0.05)
#       y = 200 + 100 * math.cos(i * 0.05)
#       pen.draw_circle(int(x), int(y), 20, Color.red, filled=True)
#
# The animation is displayed in the notebook and saved under "nanopy-output".
#
# ============================================================================


# ============================================================================
# NON-JUPYTER EXAMPLE (Standard Python)
# ============================================================================
# For standard Python scripts, use canvas.start_recording() / save_recording()
#
# To show the window while recording:
# - Call update() to display the window
# - Call update_embedded() to capture frames for MP4

import argparse
import math
import random as rnd
from collections.abc import Callable, Sequence
from importlib.resources import as_file, files
from pathlib import Path
from typing import cast

from NaNoPy import Canvas, Color, Writer
from NaNoPy.classes.moviewriter import MovieWriter

OUTPUT_DIRECTORY = Path.cwd() / "nanopy-output"


def _output_path(filename: str) -> str:
    """Return an explicit, ignored directory for generated demo videos."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    return str(OUTPUT_DIRECTORY / filename)


def example_bouncing_ball_with_export() -> None:
    """Export a bouncing ball animation to MP4 while showing the window.

    Records 300 frames at 60 FPS with ``start_recording`` / ``stop_recording``
    / ``save_recording``. Each frame is both displayed with ``update()`` and
    captured with ``update_embedded()``; leave out ``update()`` if you only
    want the video file.

    Needs ffmpeg. The result is written to ``nanopy-output/bouncing_ball.mp4``
    in the current working directory.
    """
    # Create canvas
    canvas = Canvas("Bouncing Ball", 600, 400)
    pen = Writer(canvas)

    # Start recording to file
    canvas.start_recording(_output_path("bouncing_ball.mp4"), fps=60)

    # Animation parameters
    x, y = 300, 200
    vx, vy = 5, 3
    radius = 20
    gravity = 0.2

    frame_count = 0
    max_frames = 300

    # Animation loop
    while canvas.running() and frame_count < max_frames:
        canvas.clear()

        # Physics
        vy += gravity
        x += vx
        y += vy

        # Bounce off walls
        if x - radius < 0 or x + radius > 600:
            vx *= -0.95
            x = max(radius, min(600 - radius, x))

        if y - radius < 0 or y + radius > 400:
            vy *= -0.95
            y = max(radius, min(400 - radius, y))

        # Draw
        pen.draw_circle(int(x), int(y), radius, Color.blue, filled=True)

        # Update display (shows window) AND capture frame for recording
        canvas.update()  # Show the window
        canvas.update_embedded()  # Capture frame for MP4
        canvas.pause(16)  # ~60 FPS
        frame_count += 1

    # Stop finalizes the stream; save atomically publishes the finished file.
    canvas.stop_recording()
    output_path = canvas.save_recording()
    print(f"✓ Animation exported to: {output_path}")

    canvas.NNP.stop()


def example_rotating_square() -> None:
    """Export a rotating square animation to MP4 at 30 FPS.

    The same recipe as ``mp4_bouncing_ball`` with a smaller frame budget, so it
    is the quickest way to check that your ffmpeg installation works.

    Needs ffmpeg. The result is written to ``nanopy-output/rotating_square.mp4``
    in the current working directory.
    """
    canvas = Canvas("Rotating Square", 500, 500)
    pen = Writer(canvas)

    # Start recording to file
    canvas.start_recording(_output_path("rotating_square.mp4"), fps=30)

    max_frames = 180
    frame = 0

    while canvas.running() and frame < max_frames:
        canvas.clear()

        # Rotate square
        angle = frame * 2 * math.pi / 180
        size = 80
        cx, cy = 250, 250

        # Calculate corners
        corners = []
        for i in range(4):
            corner_angle = angle + i * math.pi / 2
            x = cx + size * math.cos(corner_angle)
            y = cy + size * math.sin(corner_angle)
            corners.append((x, y))

        # Draw square
        for i in range(4):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % 4]
            pen.draw_line(x1, y1, x2, y2, Color.green)

        # Update display (shows window) AND capture frame for recording
        canvas.update()  # Show the window
        canvas.update_embedded()  # Capture frame for MP4
        canvas.pause(33)  # ~30 FPS
        frame += 1

    canvas.stop_recording()
    output_path = canvas.save_recording()
    print(f"✓ Animation exported to: {output_path}")

    canvas.NNP.stop()


def example_with_cleanup() -> None:
    """Drive a MovieWriter yourself instead of letting the canvas own it.

    Creates the ``MovieWriter``, feeds it the image returned by
    ``update_embedded()`` with ``add_frame``, and reports ``frame_count()`` and
    ``get_duration()`` afterwards. Use this when you want to decide per frame
    whether it ends up in the video.

    Needs ffmpeg. The result is written to ``nanopy-output/advanced_export.mp4``
    in the current working directory.
    """
    canvas = Canvas("Advanced Recording", 400, 300)
    pen = Writer(canvas)

    # Create MovieWriter instance
    movie = MovieWriter(_output_path("advanced_export.mp4"), fps=24)
    movie.start_recording()

    # Animation with manual frame capture
    for frame_num in range(100):
        canvas.clear()

        # Draw something
        x = 200 + 100 * math.sin(frame_num * 0.1)
        y = 150 + 50 * math.cos(frame_num * 0.1)
        pen.draw_circle(int(x), int(y), 15, Color.red, filled=True)
        # Update display and capture frame
        canvas.update()  # Show the window
        img = canvas.update_embedded()  # Capture frame
        movie.add_frame(img)

        canvas.pause(42)  # ~24 FPS

    # Save MP4
    path = movie.save()
    print(f"✓ Advanced recording saved to: {path}")
    print(f"  Frames recorded: {movie.frame_count()}")
    print(f"  Duration: {movie.get_duration():.2f} seconds")

    canvas.NNP.stop()


def example_with_audio() -> None:
    """Export a 10-second star animation with an audio track.

    Records at 240 FPS and then muxes in the short preview clip packaged with
    the demos through ``MovieWriter.save_with_audio``. All motion is expressed
    per second rather than per frame, so the animation looks the same at any
    FPS.

    Needs ffmpeg. The result is written to
    ``nanopy-output/star_animation_with_audio.mp4`` in the current working
    directory.
    """
    # Setup
    FPS = 240
    dt = 1.0 / FPS
    x_size, y_size = 1900, 1000
    y = y_size / 2
    stars = [(rnd.randint(0, x_size), rnd.randint(0, y_size)) for _ in range(500)]
    particles = []
    canvas = Canvas("Star Animation with Audio", x_size, y_size)
    pen = Writer(canvas)

    # Motion/config tuned to be time-based (fps independent)
    star_speed = 150.0  # px per second
    star_radius = 10.0 * (y_size / 540.0)
    particle_spawn_rate = 150.0  # particles per second
    particle_spawn_accum = 0.0
    particle_vx_range = (-30.0, 0.0)  # px/s
    particle_vy_range = (-15.0, 15.0)  # px/s
    particle_life_range = (0.2, 10.0)  # seconds
    pause_ms = max(1, int(1000 * dt))
    x = 0.0

    # Start recording
    movie = canvas.start_recording(_output_path("star_animation_with_audio.mp4"), fps=FPS)

    # Animation parameters
    max_frames = 10 * FPS  # 10 seconds
    frame_count = 0

    print("Recording star animation with audio...")

    while canvas.running() and frame_count < max_frames:
        canvas.clear()

        x = (x + star_speed * dt) % x_size

        # Draw background stars
        for star in stars:
            pen.draw_pixel(star[0], star[1], Color.white)

        # Add new particles at the star's position (fps independent)
        particle_spawn_accum += particle_spawn_rate * dt
        spawn_count = int(particle_spawn_accum)
        particle_spawn_accum -= spawn_count
        particles.extend(
            [
                x,
                y,
                rnd.uniform(*particle_vx_range),
                rnd.uniform(*particle_vy_range),
                rnd.uniform(*particle_life_range),
            ]
            for _ in range(spawn_count)
        )

        # Update and draw particles
        i = 0
        while i < len(particles):
            particle = particles[i]
            particle[0] += particle[2] * dt  # Update x position
            particle[1] += particle[3] * dt  # Update y position
            particle[4] -= dt  # Decrease lifetime (seconds)

            pen.draw_pixel(int(particle[0]), int(particle[1]), Color.red)

            if particle[4] <= 0:
                particles.pop(i)
            else:
                i += 1

        # Draw the star
        pen.draw_star(x, y, int(star_radius), 5, Color.yellow, True)

        # Update display and capture frame (explicitly add to movie)
        canvas.update()
        canvas.update_embedded()  # Captures frame automatically when recording
        canvas.pause(pause_ms)
        frame_count += 1

        if frame_count % FPS == 0:  # Progress every second
            print(f"  {frame_count // FPS} seconds recorded...")

    # Stop recording
    canvas.stop_recording()
    movie_writer = movie

    audio_resource = files("NaNoPy.demos").joinpath("resources/preview.mp3")
    if audio_resource.is_file():
        # ``as_file`` also works when package resources are not ordinary files.
        with as_file(audio_resource) as audio_path:
            output_path = movie_writer.save_with_audio(str(audio_path))
        print(f"✓ Animation with audio saved to: {output_path}")
        print(f"  Frames recorded: {movie_writer.frame_count()}")
        print(f"  Duration: {movie_writer.get_duration():.2f} seconds")
    else:
        print("⚠ Warning: packaged preview audio was not found")
        print("   Saving without audio instead...")
        output_path = movie_writer.save()
        print(f"✓ Animation (no audio) saved to: {output_path}")
        print(f"  Frames recorded: {movie_writer.frame_count()}")
        print(f"  Duration: {movie_writer.get_duration():.2f} seconds")

    canvas.NNP.stop()


# ============================================================================
# ADVANCED: MovieWriter features
# ============================================================================
"""
MovieWriter supports several useful methods:

1. Basic usage:
   movie = MovieWriter("output.mp4", fps=30, codec="libx265")
   movie.start_recording()
   movie.add_frame(image)
   movie.save()

2. Check recording status:
   if movie.is_recording:
       movie.add_frame(image)

3. Get recording info:
   frame_count = movie.frame_count()        # Number of frames
   duration = movie.get_duration()           # Duration in seconds

4. Clear frames:
   movie.clear()  # Free memory without saving

5. Save with audio (requires audio file):
   movie.save_with_audio("background.mp3")

6. Different codecs (select before recording because frames stream immediately):
   movie = MovieWriter("output.mp4", fps=30, codec="libx265")
   movie = MovieWriter("output.mp4", fps=30, codec="mpeg4")

7. Error handling:
   try:
       movie.save()
   except RuntimeError as e:
       print(f"Failed to save: {e}")
       print("Make sure ffmpeg is installed")
"""


_EXAMPLES: dict[str, tuple[str, Callable[[], None]]] = {
    "bouncing-ball": (
        "export a bouncing ball animation",
        example_bouncing_ball_with_export,
    ),
    "rotating-square": (
        "export a rotating square animation",
        example_rotating_square,
    ),
    "advanced": (
        "use MovieWriter directly for advanced recording control",
        example_with_cleanup,
    ),
    "audio": (
        "export a star animation with the packaged audio preview",
        example_with_audio,
    ),
}


def _build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for selecting an export example."""
    parser = argparse.ArgumentParser(
        description="Run one of NaNoPy's MP4 export examples.",
        epilog=f"Generated videos are saved under: {OUTPUT_DIRECTORY}",
    )
    subparsers = parser.add_subparsers(
        dest="example",
        metavar="EXAMPLE",
        required=True,
        title="examples",
    )
    for name, (description, runner) in _EXAMPLES.items():
        example_parser = subparsers.add_parser(name, help=description)
        example_parser.set_defaults(example_runner=runner)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Parse CLI arguments and run the selected MP4 export example."""
    arguments = _build_argument_parser().parse_args(argv)
    runner = cast("Callable[[], None]", arguments.example_runner)
    runner()


if __name__ == "__main__":
    main()
