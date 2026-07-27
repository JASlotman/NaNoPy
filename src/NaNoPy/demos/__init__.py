"""Ready-to-run NaNoPy demos.

Every demo is a normal function: import it, ask what it does, then call it.

    >>> from NaNoPy.demos import dots
    >>> help(dots)          # what does this demo show?
    >>> dots()              # run it

To see what is available, use :func:`list_demos`::

    >>> from NaNoPy.demos import list_demos
    >>> list_demos()

Installing NaNoPy also provides the ``nanopy`` command, so a demo can be run
without writing any code::

    nanopy                                 # list every demo
    nanopy dots                            # run one demo
    python -m NaNoPy dots                  # same, without the executable
    python -m NaNoPy.demos.dots            # or run the demo's own file

Drawing basics
    ``squares``, ``funky_polygons``, ``color_palette``, ``dots``

Animation and simulation
    ``randommove``, ``blobby``, ``splines``, ``nerve``, ``efficiency``

Windows and input
    ``keyboard_input``, ``multiple_windows``, ``ball_window``,
    ``multiple_ball``, ``font_bug_on_graph_window``

Collision detection
    ``collision_benchmark`` plus the individual ``collision_*`` variants

MP4 export
    ``mp4_bouncing_ball``, ``mp4_rotating_square``, ``mp4_advanced_recording``,
    ``mp4_with_audio``

Known platform problems and deprecated API
    ``mac_arm_ball``, ``mac_arm_problem``, ``warning_deprecated``
"""

from collections.abc import Callable

from NaNoPy.demos.ball_window import demo as ball_window
from NaNoPy.demos.blobby import demo as blobby
from NaNoPy.demos.collision_demo import demo as collision_benchmark
from NaNoPy.demos.collision_demo import demo_decorator_dual_ab as collision_decorator_dual_ab
from NaNoPy.demos.collision_demo import demo_decorator_single as collision_decorator_single
from NaNoPy.demos.collision_demo import demo_double_for as collision_double_for
from NaNoPy.demos.collision_demo import demo_iterator_dual_ab as collision_iterator_dual_ab
from NaNoPy.demos.collision_demo import demo_iterator_dual_by_particle_type as collision_iterator_dual_by_particle_type
from NaNoPy.demos.collision_demo import demo_iterator_single as collision_iterator_single
from NaNoPy.demos.color_palette import demo as color_palette
from NaNoPy.demos.dots import demo as dots
from NaNoPy.demos.efficiency import demo as efficiency
from NaNoPy.demos.font_bug_on_graph_window import demo as font_bug_on_graph_window
from NaNoPy.demos.funky_polygons import demo as funky_polygons
from NaNoPy.demos.input import demo as keyboard_input
from NaNoPy.demos.mac_arm_ball import demo as mac_arm_ball
from NaNoPy.demos.mac_arm_problem import demo as mac_arm_problem
from NaNoPy.demos.mp4_export_examples import example_bouncing_ball_with_export as mp4_bouncing_ball
from NaNoPy.demos.mp4_export_examples import example_rotating_square as mp4_rotating_square
from NaNoPy.demos.mp4_export_examples import example_with_audio as mp4_with_audio
from NaNoPy.demos.mp4_export_examples import example_with_cleanup as mp4_advanced_recording
from NaNoPy.demos.multiple_ball import demo as multiple_ball
from NaNoPy.demos.multiple_windows import demo as multiple_windows
from NaNoPy.demos.nerve import demo as nerve
from NaNoPy.demos.randommove import demo as randommove
from NaNoPy.demos.splines import demo as splines
from NaNoPy.demos.squares import demo as squares
from NaNoPy.demos.warning_deprecated import demo as warning_deprecated

#: Every demo by the name it is imported under. Values are callables that run
#: the demo; their docstrings explain what each one shows.
DEMOS: dict[str, Callable[..., None]] = {
    "ball_window": ball_window,
    "blobby": blobby,
    "collision_benchmark": collision_benchmark,
    "collision_decorator_dual_ab": collision_decorator_dual_ab,
    "collision_decorator_single": collision_decorator_single,
    "collision_double_for": collision_double_for,
    "collision_iterator_dual_ab": collision_iterator_dual_ab,
    "collision_iterator_dual_by_particle_type": collision_iterator_dual_by_particle_type,
    "collision_iterator_single": collision_iterator_single,
    "color_palette": color_palette,
    "dots": dots,
    "efficiency": efficiency,
    "font_bug_on_graph_window": font_bug_on_graph_window,
    "funky_polygons": funky_polygons,
    "keyboard_input": keyboard_input,
    "mac_arm_ball": mac_arm_ball,
    "mac_arm_problem": mac_arm_problem,
    "mp4_advanced_recording": mp4_advanced_recording,
    "mp4_bouncing_ball": mp4_bouncing_ball,
    "mp4_rotating_square": mp4_rotating_square,
    "mp4_with_audio": mp4_with_audio,
    "multiple_ball": multiple_ball,
    "multiple_windows": multiple_windows,
    "nerve": nerve,
    "randommove": randommove,
    "splines": splines,
    "squares": squares,
    "warning_deprecated": warning_deprecated,
}


def demo_summary(name: str) -> str:
    """Return the first line of a demo's docstring.

    Args:
        name: Key in :data:`DEMOS`.

    Returns:
        The demo's one-line summary, or a placeholder when it has no docstring.

    """
    docstring = DEMOS[name].__doc__
    if not docstring:
        return "(no description available)"
    return docstring.strip().splitlines()[0]


def list_demos() -> None:
    """Print every demo with its one-line summary.

    Use ``help(<demo>)`` for the full description of a single demo.
    """
    width = max(len(name) for name in DEMOS)
    for name in DEMOS:
        print(f"{name:<{width}}  {demo_summary(name)}")


__all__ = [
    "DEMOS",
    "ball_window",
    "blobby",
    "collision_benchmark",
    "collision_decorator_dual_ab",
    "collision_decorator_single",
    "collision_double_for",
    "collision_iterator_dual_ab",
    "collision_iterator_dual_by_particle_type",
    "collision_iterator_single",
    "color_palette",
    "demo_summary",
    "dots",
    "efficiency",
    "font_bug_on_graph_window",
    "funky_polygons",
    "keyboard_input",
    "list_demos",
    "mac_arm_ball",
    "mac_arm_problem",
    "mp4_advanced_recording",
    "mp4_bouncing_ball",
    "mp4_rotating_square",
    "mp4_with_audio",
    "multiple_ball",
    "multiple_windows",
    "nerve",
    "randommove",
    "splines",
    "squares",
    "warning_deprecated",
]
