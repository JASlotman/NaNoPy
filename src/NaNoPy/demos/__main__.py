"""Command-line entry point: ``python -m NaNoPy.demos [--list] [DEMO]``."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from NaNoPy.demos import DEMOS, demo_summary, list_demos

if TYPE_CHECKING:
    from collections.abc import Sequence


def _build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for selecting a demo."""
    parser = argparse.ArgumentParser(
        prog="python -m NaNoPy.demos",
        description="Run one of NaNoPy's demos.",
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
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Parse command-line arguments and run or list demos."""
    parser = _build_argument_parser()
    arguments = parser.parse_args(argv)

    if arguments.list:
        list_demos()
        return

    if arguments.demo is None:
        list_demos()
        parser.exit(2, "\nerror: no demo selected; pass one of the names listed above\n")

    print(f"{arguments.demo}: {demo_summary(arguments.demo)}")
    DEMOS[arguments.demo]()


if __name__ == "__main__":
    main()
