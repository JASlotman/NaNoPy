from collections import defaultdict
from itertools import combinations, product, zip_longest
from math import floor
from operator import index as operator_index
from typing import Callable, Iterable, Iterator, Optional, TypeVar


_MISSING_COORDINATE = object()
_GridSize = TypeVar("_GridSize")


def _validate_gridsize(gridsize: _GridSize) -> _GridSize:
    """Validate a grid size without converting or losing numeric precision."""

    try:
        is_positive = bool(gridsize > 0)

        finite_check = getattr(gridsize, "is_finite", None)
        if finite_check is not None:
            is_finite_value = bool(finite_check() if callable(finite_check) else finite_check)
        else:
            # For finite numeric values, subtracting a value from itself is
            # exactly zero. IEEE infinities instead produce NaN, and NaN does
            # not compare equal to zero. This avoids converting large exact
            # values (or Decimal/Fraction-like types) through binary float.
            is_finite_value = bool(gridsize - gridsize == 0)
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise ValueError("gridsize must be a finite number greater than zero") from exc

    if not is_positive or not is_finite_value:
        raise ValueError("gridsize must be a finite number greater than zero")

    return gridsize


def _iter_indexed_points(
    xs: Iterable[float],
    ys: Iterable[float],
    *,
    label: str,
) -> Iterator[tuple[int, float, float]]:
    """Consume coordinate iterables once and reject unequal lengths.

    ``zip_longest`` retains support for one-shot generators while avoiding the
    silent truncation of ordinary ``zip``.
    """

    coordinates = zip_longest(xs, ys, fillvalue=_MISSING_COORDINATE)
    for index, (x, y) in enumerate(coordinates):
        if x is _MISSING_COORDINATE or y is _MISSING_COORDINATE:
            raise ValueError(f"{label} x and y coordinate iterables must have equal lengths")
        yield index, x, y


def _floor_cell_coordinate(coordinate: float, gridsize: float) -> int:
    """Calculate one cell coordinate without rounding exact numeric values."""

    try:
        integer_coordinate = operator_index(coordinate)
        integer_gridsize = operator_index(gridsize)
    except TypeError:
        pass
    else:
        return integer_coordinate // integer_gridsize

    coordinate_ratio = getattr(coordinate, "as_integer_ratio", None)
    gridsize_ratio = getattr(gridsize, "as_integer_ratio", None)
    if callable(coordinate_ratio) and callable(gridsize_ratio):
        coordinate_numerator, coordinate_denominator = coordinate_ratio()
        gridsize_numerator, gridsize_denominator = gridsize_ratio()

        # (cn / cd) / (gn / gd) == (cn * gd) / (cd * gn). All
        # built-in ratio providers return exact integers with positive
        # denominators, and gridsize has already been validated as positive.
        return (coordinate_numerator * gridsize_denominator) // (
            coordinate_denominator * gridsize_numerator
        )

    # Retain support for custom numeric types that implement compatible
    # division and floor conversion but do not expose an exact ratio.
    return floor(coordinate / gridsize)


def _calc_chunk_id(x: float, y: float, gridsize: float) -> tuple[int, int]:
    """Map a point to its grid cell using floor division semantics."""

    return _floor_cell_coordinate(x, gridsize), _floor_cell_coordinate(y, gridsize)


def _get_chunk_id_neighbors(chunk_id: tuple[int, int]) -> Iterator[tuple[int, int]]:
    """Yield a cell and all eight cells directly adjacent to it."""

    i_range = range(chunk_id[0] - 1, chunk_id[0] + 2)
    j_range = range(chunk_id[1] - 1, chunk_id[1] + 2)
    yield from product(i_range, j_range)


def get_close_pairs(
    xs_A: Iterable[float],
    ys_A: Iterable[float],
    gridsize: float,
    xs_B: Optional[Iterable[float]] = None,
    ys_B: Optional[Iterable[float]] = None,
) -> Iterator[tuple[int, int]]:
    """Return candidate pairs from the same or directly adjacent grid cells.

    This is a broad-phase spatial query, not a Euclidean-distance test. A cell
    is ``(floor(x / gridsize), floor(y / gridsize))`` and its eight surrounding
    cells are considered adjacent.

    With only A coordinates, each unordered AA pair is yielded exactly once as
    ``(lower_index, higher_index)``. When both B coordinate iterables are
    supplied, ordered ``(A_index, B_index)`` pairs are yielded instead. The x
    and y iterables for each particle set must have equal lengths; one-shot
    iterables and generators are supported and consumed exactly once. Numeric
    values are not coerced to float, so mutually compatible exact types such as
    large integers, ``Decimal``, and ``Fraction`` retain their precision.

    Args:
        xs_A: X coordinates for particle set A.
        ys_A: Y coordinates for particle set A.
        gridsize: Finite, positive width and height of every grid cell.
        xs_B: Optional X coordinates for particle set B.
        ys_B: Optional Y coordinates for particle set B.

    Raises:
        ValueError: If ``gridsize`` is not finite and positive, only one B
            iterable is supplied, or an x/y coordinate pair has unequal
            lengths.
    """

    validated_gridsize = _validate_gridsize(gridsize)

    if (xs_B is None) != (ys_B is None):
        raise ValueError("xs_B and ys_B must be provided together")

    if xs_B is None:
        return _get_close_AA_pairs(xs_A, ys_A, validated_gridsize)

    return _get_close_AB_pairs(xs_A, ys_A, xs_B, ys_B, validated_gridsize)


def get_close_AB_pairs(
    xs_A: Iterable[float],
    ys_A: Iterable[float],
    xs_B: Iterable[float],
    ys_B: Iterable[float],
    gridsize: float,
) -> Iterator[tuple[int, int]]:
    """Return ``(A_index, B_index)`` candidates in neighboring grid cells."""

    validated_gridsize = _validate_gridsize(gridsize)
    return _get_close_AB_pairs(xs_A, ys_A, xs_B, ys_B, validated_gridsize)


def _get_close_AB_pairs(
    xs_A: Iterable[float],
    ys_A: Iterable[float],
    xs_B: Iterable[float],
    ys_B: Iterable[float],
    gridsize: float,
) -> Iterator[tuple[int, int]]:
    particles_by_chunk: dict[tuple[int, int], list[int]] = defaultdict(list)

    for j, x, y in _iter_indexed_points(xs_B, ys_B, label="B"):
        particles_by_chunk[_calc_chunk_id(x, y, gridsize)].append(j)

    # Consume and validate both A coordinate iterables before yielding any
    # pairs, so a late length mismatch cannot produce partially applied work.
    particles_A = [
        (i, _calc_chunk_id(x, y, gridsize))
        for i, x, y in _iter_indexed_points(xs_A, ys_A, label="A")
    ]

    for i, own_chunk_id in particles_A:
        for chunk_id in _get_chunk_id_neighbors(own_chunk_id):
            for j in particles_by_chunk.get(chunk_id, ()):
                yield i, j


def get_close_AA_pairs(
    xs_A: Iterable[float],
    ys_A: Iterable[float],
    gridsize: float,
) -> Iterator[tuple[int, int]]:
    """Return each unordered AA candidate from neighboring cells once."""

    validated_gridsize = _validate_gridsize(gridsize)
    return _get_close_AA_pairs(xs_A, ys_A, validated_gridsize)


def _get_close_AA_pairs(
    xs_A: Iterable[float],
    ys_A: Iterable[float],
    gridsize: float,
) -> Iterator[tuple[int, int]]:
    particles_by_chunk: dict[tuple[int, int], list[int]] = defaultdict(list)

    for i, x, y in _iter_indexed_points(xs_A, ys_A, label="A"):
        particles_by_chunk[_calc_chunk_id(x, y, gridsize)].append(i)

    for chunk_id, own_indices in particles_by_chunk.items():
        yield from combinations(own_indices, 2)

        # Tuple ordering selects one half of the eight neighboring cells, so
        # cross-cell pairs cannot be emitted twice.
        for neighbor_id in _get_chunk_id_neighbors(chunk_id):
            if neighbor_id <= chunk_id:
                continue

            neighbor_indices = particles_by_chunk.get(neighbor_id)
            if not neighbor_indices:
                continue

            for i, j in product(own_indices, neighbor_indices):
                yield (i, j) if i < j else (j, i)


def apply_to_close_pairs(
    xs_A: Iterable[float],
    ys_A: Iterable[float],
    gridsize: float,
    xs_B: Optional[Iterable[float]] = None,
    ys_B: Optional[Iterable[float]] = None,
) -> Callable[[Callable[[int, int], object]], None]:
    """Apply a decorated function once to every candidate pair.

    Omitting both B iterables applies the function to AA pairs. Supplying both
    applies it to ordered AB pairs. Validation and cell semantics are identical
    to :func:`get_close_pairs`.
    """

    close_pairs = get_close_pairs(xs_A, ys_A, gridsize, xs_B, ys_B)

    def decorator(func: Callable[[int, int], object]) -> None:
        for i, j in close_pairs:
            func(i, j)

    return decorator
