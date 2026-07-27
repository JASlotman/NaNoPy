# NaNoPy

NaNoPy is a PySDL2-based graphical engine used in the Nanobiology program of
Erasmus MC/TU Delft.

## Demos

Every demo is an importable function whose docstring explains what it shows:

```python
from NaNoPy.demos import dots

help(dots)   # what does this demo show?
dots()       # run it
```

To see what is available:

```python
from NaNoPy.demos import list_demos

list_demos()
```

The same demos run from the command line, so no source file ever has to be
edited to pick one:

```sh
python -m NaNoPy.demos --list      # list every demo
python -m NaNoPy.demos dots        # run one demo
python -m NaNoPy.demos.dots        # or run that demo's own file
```

## Documentation

- [Correctness and lifecycle guarantees](docs/correctness-and-lifecycle.md)
  documents SDL initialization and cleanup, color representation, collision
  candidate selection, and the public drawing coordinate system.

The packaged demo audio preview is derived from
["Preview sound" by envirOmaniac2](https://freesound.org/people/envirOmaniac2/sounds/467494/).
