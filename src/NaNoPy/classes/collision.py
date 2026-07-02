from itertools import combinations, product, chain
from collections import defaultdict
from typing import Iterator, Callable, Iterable
from math import floor

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

def get_close_pairs(xs:Iterable[float], ys:Iterable[float], gridsize:float) -> Iterator[tuple[int,int]]:
    """
    Function for getting all unique pairs (x1, y1) (x2, y2) that are in 
    neiboring or the same grid cells. 
    """
    particle_dictionary:dict[tuple[int,int], list[int]] = defaultdict(list)

    for i, (x, y) in enumerate(zip(xs, ys)):
        own_chunk_id = _calc_chunk_id(x, y, gridsize)
        for neighbor_id in _get_chunk_id_neighbors(own_chunk_id):
            particle_dictionary[neighbor_id].append(i)

    pairs = set().union(chain.from_iterable(combinations(subset,2) for subset in particle_dictionary.values()))

    yield from pairs

def apply_to_close_pairs(
    xs:Iterable[float], ys:Iterable[float], gridsize:int
) -> Callable[[Callable[[int, int], object]], None]:
    """
    Decorator that calls function `func` for all pairs of indices i, j such that
    (xs[i], ys[i]) is close to (xs[j], ys[j]). 
    """
    close_pairs = get_close_pairs(xs, ys, gridsize)

    def decorator(func:Callable[[int, int], object]) -> None:
        for i, j in close_pairs:
            func(i, j)

    return decorator
