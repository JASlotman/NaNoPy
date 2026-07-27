# NaNoPy

NaNoPy is a PySDL2-based graphical engine used in the Nanobiology program of
Erasmus MC/TU Delft.

## Demos

Installing NaNoPy installs the `nanopy` command, so no source file ever has to
be edited to run a demo:

```sh
nanopy                 # list every demo with a one-line description
nanopy dots            # run one demo
nanopy --version
```

`NaNoPy` works as a command name too, and `python -m NaNoPy` does the same when
the executable is not on your `PATH`.

Every demo is also an importable function whose docstring explains what it
shows:

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

Each demo is a standalone script as well, so it can still be run on its own:

```sh
python -m NaNoPy.demos.dots
```

## Documentation

- [Correctness and lifecycle guarantees](docs/correctness-and-lifecycle.md)
  documents SDL initialization and cleanup, color representation, collision
  candidate selection, and the public drawing coordinate system.

The packaged demo audio preview is derived from
["Preview sound" by envirOmaniac2](https://freesound.org/people/envirOmaniac2/sounds/467494/).
