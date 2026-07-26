import unittest
from typing import TYPE_CHECKING, cast
from unittest.mock import Mock

from NaNoPy import Color
from NaNoPy.demos.color_palette import _draw_checkerboard, _draw_text_with_stroke

if TYPE_CHECKING:
    from collections.abc import Iterable


class ColorPaletteDemoTests(unittest.TestCase):
    def test_checkerboard_draws_alternating_eight_pixel_tiles(self) -> None:
        writer = Mock()

        _draw_checkerboard(writer, width=16, height=16)

        self.assertEqual(writer.draw_rectangle.call_count, 4)
        calls = writer.draw_rectangle.call_args_list
        self.assertEqual([call.args[:4] for call in calls], [(0, 0, 8, 8), (8, 0, 8, 8), (0, 8, 8, 8), (8, 8, 8, 8)])
        self.assertEqual(
            [tuple(call.args[4]) for call in calls],
            [
                (96, 96, 96, 255),
                (160, 160, 160, 255),
                (160, 160, 160, 255),
                (96, 96, 96, 255),
            ],
        )
        self.assertTrue(all(call.kwargs == {"filled": True} for call in calls))

    def test_text_stroke_surrounds_the_foreground_label(self) -> None:
        writer = Mock()

        _draw_text_with_stroke(writer, 10, 20, "black")

        calls = writer.draw_string.call_args_list
        self.assertEqual(len(calls), 9)
        self.assertEqual(
            [call.args[:2] for call in calls[:-1]],
            [(9, 19), (10, 19), (11, 19), (9, 20), (11, 20), (9, 21), (10, 21), (11, 21)],
        )
        black = tuple(cast("Iterable[int]", Color.black))
        self.assertTrue(all(tuple(call.args[2]) == black for call in calls[:-1]))
        self.assertTrue(all(call.args[3] == "black" for call in calls[:-1]))
        self.assertEqual(calls[-1].args[:2], (10, 20))
        self.assertEqual(tuple(calls[-1].args[2]), tuple(cast("Iterable[int]", Color.white)))
        self.assertEqual(calls[-1].args[3], "black")


if __name__ == "__main__":
    unittest.main()
