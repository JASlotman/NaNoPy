from decimal import Decimal, localcontext
from fractions import Fraction
import math
import random
import unittest

from NaNoPy.collisions import (
    _calc_chunk_id,
    get_close_AB_pairs,
    get_close_AA_pairs,
    get_close_pairs,
)


class CollisionPairTests(unittest.TestCase):
    @staticmethod
    def exact_floor_ratio(value, gridsize):
        value_numerator, value_denominator = value.as_integer_ratio()
        grid_numerator, grid_denominator = gridsize.as_integer_ratio()
        return (value_numerator * grid_denominator) // (value_denominator * grid_numerator)

    def assert_pairs(self, actual, expected):
        pairs = list(actual)
        self.assertEqual(set(pairs), set(expected))
        self.assertEqual(len(pairs), len(set(pairs)), "candidate pairs must not be duplicated")

    def test_aa_pairs_only_same_or_adjacent_cells(self):
        # Chunks are (0, 0), (0, 0), (1, 0), and (2, 0). The old
        # neighbor-expanded buckets incorrectly paired chunks 0 and 2.
        self.assert_pairs(
            get_close_pairs([0.1, 0.9, 1.1, 2.1], [0.1] * 4, 1.0),
            {(0, 1), (0, 2), (1, 2), (2, 3)},
        )

    def test_aa_handles_negative_cells_and_exact_boundaries(self):
        # floor(-1.0 / 1.0) == -1 and floor(0.0 / 1.0) == 0, so these
        # boundary points are adjacent. The point in chunk 2 is not.
        self.assert_pairs(
            get_close_AA_pairs([-1.0, 0.0, 2.0], [0.0, 0.0, 0.0], 1.0),
            {(0, 1)},
        )

        # A value just below -1 belongs to chunk -2, not chunk -1.
        self.assert_pairs(
            get_close_pairs([-1.0001, 0.0], [0.0, 0.0], 1.0),
            set(),
        )

    def test_ab_pairs_are_ordered_and_support_generators(self):
        xs_A = (value for value in [0.1, -1.1])
        ys_A = (value for value in [0.1, -1.1])
        xs_B = (value for value in [1.1, 2.1, -0.1])
        ys_B = (value for value in [1.1, 0.1, -0.1])

        self.assert_pairs(
            get_close_pairs(xs_A, ys_A, 1.0, xs_B, ys_B),
            {(0, 0), (0, 2), (1, 2)},
        )

    def test_direct_ab_function_uses_the_same_cell_rules(self):
        self.assert_pairs(
            get_close_AB_pairs([0.1], [0.1], [1.1, 2.1], [1.1, 0.1], 1.0),
            {(0, 0)},
        )

    def test_integer_cell_classification_is_exact_above_two_to_the_53(self):
        gridsize = 2**53 + 1

        # gridsize - 1 is in cell 0 and 2 * gridsize is in cell 2. Coercing
        # gridsize to float rounds it down and incorrectly makes these cells
        # appear adjacent.
        self.assert_pairs(
            get_close_pairs([gridsize - 1, 2 * gridsize], [0, 0], gridsize),
            set(),
        )

    def test_huge_finite_integer_gridsize_does_not_overflow_validation(self):
        gridsize = 10**1000
        self.assert_pairs(
            get_close_pairs([0, 2 * gridsize], [0, 0], gridsize),
            set(),
        )

    def test_decimal_coordinates_and_gridsize_keep_decimal_precision(self):
        gridsize = Decimal("0.1")
        self.assert_pairs(
            get_close_pairs(
                [Decimal("0.099"), Decimal("0.2"), Decimal("-0.1")],
                [Decimal("0"), Decimal("0"), Decimal("0")],
                gridsize,
            ),
            {(0, 2)},
        )

    def test_decimal_context_rounding_cannot_cross_a_cell_boundary(self):
        gridsize = Decimal("1")
        just_below_one = Decimal("0." + "9" * 29)

        # Decimal's default 28-digit context rounds just_below_one / 1 to
        # exactly 1. Cell classification must instead use its exact value,
        # which belongs to cell 0 and is not adjacent to the point in cell 2.
        with localcontext() as context:
            context.prec = 28
            self.assertEqual(just_below_one / gridsize, Decimal("1"))
            self.assert_pairs(
                get_close_pairs(
                    [just_below_one, Decimal("2")],
                    [Decimal("0"), Decimal("0")],
                    gridsize,
                ),
                set(),
            )

    def test_fraction_coordinates_and_gridsize_remain_exact(self):
        gridsize = Fraction(1, 3)
        self.assert_pairs(
            get_close_pairs(
                [gridsize - Fraction(1, 100), 2 * gridsize],
                [Fraction(0), Fraction(0)],
                gridsize,
            ),
            set(),
        )

    def test_randomized_decimal_and_fraction_cells_match_exact_ratios(self):
        rng = random.Random(20260723)

        for _ in range(100):
            scale = rng.randrange(0, 10)
            extra_digits = rng.randrange(29, 61)
            gridsize = Decimal(f"1e-{scale}")

            # Construct values just below randomly selected cell boundaries
            # directly from decimal strings, avoiding context-rounded setup.
            x_boundary = rng.randrange(-1000, 1001)
            y_boundary = rng.randrange(-1000, 1001)
            x_coefficient = x_boundary * 10**extra_digits - 1
            y_coefficient = y_boundary * 10**extra_digits - 1
            x = Decimal(f"{x_coefficient}e-{scale + extra_digits}")
            y = Decimal(f"{y_coefficient}e-{scale + extra_digits}")

            self.assertEqual(
                _calc_chunk_id(x, y, gridsize),
                (
                    self.exact_floor_ratio(x, gridsize),
                    self.exact_floor_ratio(y, gridsize),
                ),
            )

        for _ in range(100):
            gridsize = Fraction(rng.randrange(1, 10**12), rng.randrange(1, 10**12))
            x = Fraction(rng.randrange(-(10**20), 10**20), rng.randrange(1, 10**12))
            y = Fraction(rng.randrange(-(10**20), 10**20), rng.randrange(1, 10**12))

            self.assertEqual(
                _calc_chunk_id(x, y, gridsize),
                (
                    self.exact_floor_ratio(x, gridsize),
                    self.exact_floor_ratio(y, gridsize),
                ),
            )

    def test_rejects_non_positive_or_non_finite_gridsize(self):
        for gridsize in (
            0,
            -1,
            math.nan,
            math.inf,
            -math.inf,
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        ):
            with self.subTest(gridsize=gridsize):
                with self.assertRaisesRegex(ValueError, "finite number greater than zero"):
                    get_close_pairs([0.0], [0.0], gridsize)

    def test_requires_both_b_coordinate_iterables(self):
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            get_close_pairs([0.0], [0.0], 1.0, xs_B=[0.0])

        with self.assertRaisesRegex(ValueError, "must be provided together"):
            get_close_pairs([0.0], [0.0], 1.0, ys_B=[0.0])

    def test_rejects_mismatched_a_coordinate_lengths(self):
        xs_A = (value for value in [0.0, 1.0])
        ys_A = (value for value in [0.0])

        with self.assertRaisesRegex(ValueError, "A x and y coordinate iterables"):
            list(get_close_pairs(xs_A, ys_A, 1.0))

    def test_rejects_mismatched_b_coordinate_lengths(self):
        xs_B = (value for value in [0.0, 1.0])
        ys_B = (value for value in [0.0])

        with self.assertRaisesRegex(ValueError, "B x and y coordinate iterables"):
            list(get_close_pairs([0.0], [0.0], 1.0, xs_B, ys_B))


if __name__ == "__main__":
    unittest.main()
