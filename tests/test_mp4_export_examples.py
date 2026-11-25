"""Tests for the MP4 export example command-line interface."""

from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch

from NaNoPy.demos import mp4_export_examples


class Mp4ExportExamplesCliTests(unittest.TestCase):
    """Verify examples can be selected without editing the demo source."""

    def test_main_runs_only_the_selected_example(self) -> None:
        calls: list[str] = []
        examples = {
            "first": ("run the first example", lambda: calls.append("first")),
            "second": ("run the second example", lambda: calls.append("second")),
        }

        with patch.object(mp4_export_examples, "_EXAMPLES", examples):
            mp4_export_examples.main(["second"])

        self.assertEqual(calls, ["second"])

    def test_help_lists_examples_without_running_one(self) -> None:
        output = StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            mp4_export_examples.main(["--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("bouncing-ball", output.getvalue())
        self.assertIn("rotating-square", output.getvalue())
        self.assertIn("advanced", output.getvalue())
        self.assertIn("audio", output.getvalue())

    def test_missing_example_is_rejected_without_running_one(self) -> None:
        errors = StringIO()

        with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
            mp4_export_examples.main([])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("the following arguments are required: EXAMPLE", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
