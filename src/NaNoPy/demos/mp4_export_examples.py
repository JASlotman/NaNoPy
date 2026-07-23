"""
MP4 Export Examples for NaNoPy

This file demonstrates how to export animations as MP4 videos in both
Jupyter notebook and non-Jupyter (standard Python) modes.

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
#
#   @loop(frame_count=120, xSize=400, ySize=400, record_mp4="my_animation.mp4", fps=30)
#   def animated_circle(screen: Canvas, pen: Writer, i: int):
#       x = 200 + 100 * math.sin(i * 0.05)
#       y = 200 + 100 * math.cos(i * 0.05)
#       pen.draw_circle(int(x), int(y), 20, Color.red, filled=True)
#
# The animation will be displayed in the notebook AND saved to "my_animation.mp4"
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

from NaNoPy import Canvas, Writer, Color
import math


def example_bouncing_ball_with_export():
    """Example: Export a bouncing ball animation as MP4

    Shows the animation window while recording.
    Uses update() to display + update_embedded() to capture frames.
    """

    # Create canvas
    canvas = Canvas("Bouncing Ball", 600, 400)
    pen = Writer(canvas)

    # Start recording to file
    canvas.start_recording("bouncing_ball.mp4", fps=60)

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


def example_rotating_square():
    """Example: Export a rotating square animation

    Shows the animation window while recording.
    """

    canvas = Canvas("Rotating Square", 500, 500)
    pen = Writer(canvas)

    # Start recording to file
    canvas.start_recording("rotating_square.mp4", fps=30)

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


def example_with_cleanup():
    """Example showing how to use MovieWriter directly for advanced control"""

    from NaNoPy.classes.moviewriter import MovieWriter

    canvas = Canvas("Advanced Recording", 400, 300)
    pen = Writer(canvas)

    # Create MovieWriter instance
    movie = MovieWriter("advanced_export.mp4", fps=24)
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


def example_with_audio():
    """Example: Star animation with audio track

    Creates a 10-second animation with background music.
    Requires an 'a.mp3' file in the same directory.
    """
    import random as rnd

    # Setup
    FPS = 240
    dt = 1.0 / FPS
    x_size, y_size = 1900, 1000
    y = y_size / 2
    stars = []
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
    movie = canvas.start_recording("star_animation_with_audio.mp4", fps=FPS)

    # Create background stars
    for i in range(500):
        stars.append((rnd.randint(0, x_size), rnd.randint(0, y_size)))

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
        for _ in range(spawn_count):
            particles.append(
                [
                    x,
                    y,
                    rnd.uniform(*particle_vx_range),
                    rnd.uniform(*particle_vy_range),
                    rnd.uniform(*particle_life_range),
                ]
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

    import os

    if os.path.exists("a.mp3"):
        output_path = movie_writer.save_with_audio("a.mp3")
        print(f"✓ Animation with audio saved to: {output_path}")
        print(f"  Frames recorded: {movie_writer.frame_count()}")
        print(f"  Duration: {movie_writer.get_duration():.2f} seconds")
    else:
        print("⚠ Warning: 'a.mp3' file not found in current directory")
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


if __name__ == "__main__":
    print("MP4 Export Examples")
    print("=" * 50)
    print("\nUncomment one of the function calls below to run an example:")
    print("  - example_bouncing_ball_with_export()")
    print("  - example_rotating_square()")
    print("  - example_with_cleanup()")
    print("  - example_with_audio()  # Requires 'a.mp3' file")
    print("\nEach will save an MP4 file to the current directory.")
    # example_bouncing_ball_with_export()
    # example_rotating_square()
    # example_with_cleanup()
    example_with_audio()
