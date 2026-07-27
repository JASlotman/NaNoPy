"""Tests for importing demos as ``from NaNoPy.demos import <demo>``."""

from __future__ import annotations

import importlib
import pkgutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch

import NaNoPy.demos as demos_package
from NaNoPy import NNP, cli
from NaNoPy import __main__ as nanopy_main
from NaNoPy.demos import DEMOS, dots, list_demos, squares
from NaNoPy.demos import __main__ as demos_main


class DemoImportTests(unittest.TestCase):
    """Verify the importable demo API students are told to use."""

    def test_demos_are_importable_by_name(self) -> None:
        self.assertTrue(callable(dots))
        self.assertTrue(callable(squares))

    def test_every_demo_is_callable_and_documented(self) -> None:
        for name, runner in DEMOS.items():
            with self.subTest(demo=name):
                self.assertTrue(callable(runner), f"{name} is not callable")
                docstring = runner.__doc__
                self.assertTrue(docstring, f"{name} has no docstring to show students")
                assert docstring is not None
                self.assertTrue(docstring.strip(), f"{name} has an empty docstring")

    def test_registry_matches_public_names(self) -> None:
        exported_callables = {
            name for name in demos_package.__all__ if callable(getattr(demos_package, name)) and name not in {"demo_summary", "list_demos"}
        }
        self.assertEqual(set(DEMOS), exported_callables)
        for name in DEMOS:
            with self.subTest(demo=name):
                self.assertIs(getattr(demos_package, name), DEMOS[name])

    def test_importing_demos_opens_no_window(self) -> None:
        """Importing a demo must never create a canvas or initialize SDL."""
        for module_info in pkgutil.iter_modules(demos_package.__path__):
            with self.subTest(module=module_info.name):
                importlib.import_module(f"NaNoPy.demos.{module_info.name}")

        self.assertEqual(NNP.canvasses, {})
        self.assertFalse(NNP._sdl_initialized)

    def test_every_demo_module_runs_standalone(self) -> None:
        """Each demo file keeps its ``if __name__ == "__main__"`` entry point."""
        for module_info in pkgutil.iter_modules(demos_package.__path__):
            if module_info.name == "__main__":
                continue
            with self.subTest(module=module_info.name):
                module = importlib.import_module(f"NaNoPy.demos.{module_info.name}")
                source = module.__loader__.get_source(module.__name__)  # type: ignore[union-attr]
                assert source is not None
                self.assertIn('if __name__ == "__main__":', source)

    def test_list_demos_prints_a_line_per_demo(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            list_demos()

        printed = output.getvalue().splitlines()
        self.assertEqual(len(printed), len(DEMOS))
        for name in DEMOS:
            self.assertTrue(
                any(line.startswith(f"{name} ") or line == name for line in printed),
                f"{name} is missing from list_demos() output",
            )


class NanopyCommandTests(unittest.TestCase):
    """Verify the ``nanopy`` command selects demos without editing code."""

    def test_named_demo_is_run(self) -> None:
        calls: list[str] = []
        output = StringIO()

        with patch.dict(cli.DEMOS, {"dots": lambda: calls.append("dots")}), redirect_stdout(output):
            cli.main(["dots"])

        self.assertEqual(calls, ["dots"])

    def test_list_option_runs_nothing(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            cli.main(["--list"])

        self.assertIn("dots", output.getvalue())

    def test_no_argument_lists_every_demo(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            cli.main([])

        printed = output.getvalue()
        for name in DEMOS:
            self.assertIn(name, printed)

    def test_unknown_demo_is_rejected(self) -> None:
        errors = StringIO()

        with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
            cli.main(["does-not-exist"])

        self.assertEqual(raised.exception.code, 2)

    def test_version_is_reported(self) -> None:
        output = StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            cli.main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("NaNoPy", output.getvalue())

    def test_module_entry_points_share_the_cli(self) -> None:
        """``python -m NaNoPy`` and ``python -m NaNoPy.demos`` reuse ``cli.main``."""
        self.assertIs(nanopy_main.main, cli.main)
        self.assertIs(demos_main.main, cli.main)


if __name__ == "__main__":
    unittest.main()
