"""The ``nanopy`` command: ``nanopy [--list] [DEMO]``.

Installing NaNoPy provides a ``nanopy`` executable (``NaNoPy`` works too), so a
demo can be run without writing any code::

    nanopy               # list every demo
    nanopy dots          # run one demo

The same interface is available as ``python -m NaNoPy`` when the executable is
not on your PATH.
"""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from NaNoPy.demos import DEMOS, demo_summary, list_demos

if TYPE_CHECKING:
    from collections.abc import Sequence


def _installed_version() -> str:
    """Return the installed NaNoPy version, or a placeholder in a source tree."""
    try:
        return version("NaNoPy")
    except PackageNotFoundError:  # pragma: no cover - NaNoPy is not installed
        return "unknown (running from a source tree)"


def _build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for selecting a demo."""
    parser = argparse.ArgumentParser(
        prog="nanopy",
        description="Run one of NaNoPy's demos. Without arguments, every demo is listed.",
        epilog="Use help(<demo>) in Python for the full description of a demo.",
    )
    parser.add_argument(
        "demo",
        nargs="?",
        choices=sorted(DEMOS),
        metavar="DEMO",
        help="which demo to run; omit it to list the available demos",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list every demo with a one-line description and exit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"NaNoPy {_installed_version()}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Parse command-line arguments and run or list demos."""
    arguments = _build_argument_parser().parse_args(argv)

    if arguments.list or arguments.demo is None:
        print()
        print("For help run `nanopy --help` or `python -m NaNoPy --help`")
        print("Available NaNoPy demos. Run one with: nanopy <DEMO>")
        print()
        list_demos()
        return

    print(f"{arguments.demo}: {demo_summary(arguments.demo)}")
    DEMOS[arguments.demo]()


if __name__ == "__main__":
    main()
