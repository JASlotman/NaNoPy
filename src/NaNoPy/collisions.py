
from itertools import combinations, product, chain
from collections import defaultdict
from typing import Iterator, Iterable, Optional
from math import floor
from typing import Callable

def _calc_chunk_id(x:float, y:float, gridsize:float) -> tuple[int,int]:
    """
    Function for calculating a unique chunk-id from a particle position.
    Makes use of the fact that tuples can act as dictionary keys.
    """

    return floor(x / gridsize), floor(y / gridsize)

def _get_chunk_id_neighbors(chunk_id:tuple[int,int]) -> Iterator[tuple[int,int]]:
    """
    Function for getting all neighbors of a chunk_id. Also returns chunks
    outside of the screen, but that should not matter. Would have to clip
    the ranges using min and max statements to avoid that.
    """

    i_range = range(chunk_id[0] - 1, chunk_id[0] + 2)
    j_range = range(chunk_id[1] - 1, chunk_id[1] + 2)

    yield from product(i_range, j_range)

def get_close_pairs(
        xs_A:Iterable[float],
        ys_A:Iterable[float],
        gridsize:float,
        xs_B:Optional[Iterable[float]]=None,
        ys_B:Optional[Iterable[float]]=None
        ) -> Iterator[tuple[int,int]]:
    """
    Yields all possible ordered pairs of particles in adjacent grid cells. If
    xs_B and ys_B are supplied, only form pairs of type AB.

    Output if no xs_B or ys_B supplied: Iterator of tuples[i,j], where i is the
    index of the first particle and j is the index of the second particle in the
    input iterable.

    Output if xs_B and ys_B are both supplied: Iterator of tuples[i,j], where i
    is the index of the A-type particle and j is the index of the B-type
    particle in their respective input iterables.
    """

    if xs_B is None or ys_B is None:
        pairlist_iterator = get_close_AA_pairs(xs_A,ys_A,gridsize)
    else:
        pairlist_iterator = get_close_AB_pairs(xs_A,ys_A,xs_B,ys_B,gridsize)

    yield from pairlist_iterator

def get_close_AB_pairs(
        xs_A:Iterable[float],
        ys_A:Iterable[float],
        xs_B:Iterable[float],
        ys_B:Iterable[float],
        gridsize:float
        ) -> Iterator[tuple[int,int]]:
    """
    Yields all possible ordered pairs of type AB of particles in adjacent grid
    cells.

    Output: Iterator of tuples[i,j], where i is the index of the A-type particle
    and j is the index of the B-type particle in their respective iterable.
    """

    particle_dictionary:dict[tuple[int,int], list[int]] = defaultdict(list)
    pairlist:list[tuple[int,int]] = []

    for j, (x,y) in enumerate(zip(xs_B,ys_B)):
        own_chunk_id = _calc_chunk_id(x, y, gridsize)
        particle_dictionary[own_chunk_id].append(j)

    for i, (x,y) in enumerate(zip(xs_A,ys_A)):
        own_chunk_id = _calc_chunk_id(x, y, gridsize)
        chunks = _get_chunk_id_neighbors(own_chunk_id)
        for chunck in chunks:
            pairlist.extend( [(i,j) for j in particle_dictionary[chunck]] )

    yield from pairlist

def get_close_AA_pairs(
        xs_A:Iterable[float],
        ys_A:Iterable[float],
        gridsize:float
        ) -> Iterator[tuple[int,int]]:

    """
    Yields all possible ordered pairs particles in adjacent grid cells.

    Output: Iterator of tuples[i,j], where i is the index of the A-type particle
    and j is the index of the B-type particle in their respective iterable.
    """

    particle_dictionary:dict[tuple[int,int], list[int]] = defaultdict(list)

    for i, (x, y) in enumerate(zip(xs_A, ys_A)):
        own_chunk_id = _calc_chunk_id(x, y, gridsize)
        for neighbor_id in _get_chunk_id_neighbors(own_chunk_id):
            particle_dictionary[neighbor_id].append(i)

    pairs = set().union(chain.from_iterable(combinations(subset,2) for subset in particle_dictionary.values()))

    yield from pairs

def apply_to_close_pairs(
    xs_A:Iterable[float],
    ys_A:Iterable[float],
    gridsize:float,
    xs_B:Optional[Iterable[float]]=None,
    ys_B:Optional[Iterable[int]]=None
    ) -> Callable[[Callable[[int, int], object]], None]:

    """
    If xs_B or xs_y is not supplied: Decorator that calls function `func` for
    all pairs of indices i, j such that (xs[i], ys[i]) is close to
    (xs[j], ys[j]).

    If xs_B and xs_y are both supplied: Decorator that calls function `func` for
    all pairs of indices i, j such that (xs_A[i], ys_A[i]) is close to
    (xs_B[j], ys_B[j]).
    """

    close_pairs = get_close_pairs(xs_A, ys_A, gridsize, xs_B, ys_B)

    def decorator(func:Callable[[int, int], object]) -> None:
        for i, j in close_pairs:
            func(i, j)

    return decorator
