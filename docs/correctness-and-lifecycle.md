# Correctness and lifecycle guarantees

This note records the behavior made explicit during the final refactor audit.
It is both an API reference and a migration note for code that accidentally
depended on earlier edge-case behavior.

## SDL initialization and failures

Importing `NaNoPy` constructs the shared `NNP` mainloop object but does not
initialize SDL, create a window, or replace process signal handlers. SDL video
initialization happens when the first `Canvas` is constructed.

Canvas construction is transactional:

1. Its name must be unique among that mainloop's active canvases.
2. SDL video initialization must succeed.
3. The SDL window must be created.
4. The renderer must be created.
5. A target texture must be created and configured.
6. Only then is the canvas registered with the mainloop.

Failure during SDL initialization, allocation, or configuration raises
`RuntimeError` containing SDL's diagnostic and destroys resources created by
earlier steps. When the default renderer is requested, NaNoPy first requests
the normal accelerated renderer and then tries a target-capable software
renderer. An explicitly selected driver is not silently replaced with a
different one.

SDL subsystem initialization is reference-counted. Each active `Mainloop`
acquires and releases one video reference, so independent mainloops and other
SDL users cannot shut one another down.

## Reusable mainloop lifecycle

`Mainloop.stop()` is idempotent. It finalizes an active recording, destroys
canvas textures, renderers, and windows, clears canvas and listener
registries, and marks the loop as stopped. Creating another canvas lazily
initializes the stopped mainloop again.

NaNoPy does not install SIGINT or SIGTERM handlers. Host applications and
notebooks retain their existing signal policy; application code that catches
`KeyboardInterrupt` should call `stop()` from `finally` when it needs immediate
cleanup.

Duplicate active canvas names raise `ValueError` before a new SDL window is
allocated. This prevents replacing the registry entry while leaving the old
window, renderer, and texture unreachable.

SDL window and renderer resources are thread-affine on supported backends.
Canvas rendering and `Mainloop.stop()` must therefore run on the thread that
created the first currently active canvas. A cross-thread call raises
`RuntimeError` before native resources are touched.

Closing a window is normal control flow, not an exception. `Canvas.update()`
returns `False` when close processing stops the loop. Any `clear()` or Writer
drawing calls left later in that same animation iteration become safe no-ops,
so the common `while canvas.running(): ... update(); clear()` pattern exits
quietly. `update_embedded()` returns a black final image without reading a
destroyed renderer. Independent mainloops route all window-scoped events by
SDL window ID, so they neither close one another's windows nor deliver another
window's keyboard, text, mouse, drop, or user events to the wrong listeners.

## Color representation

All `Color` factories and properties use conventional RGBA order:

```python
color = Color.custom(r=10, g=20, b=30, a=40)
assert (color.r, color.g, color.b, color.a) == (10, 20, 30, 40)
```

SDL_gfx's packed-color functions read the four native `Uint32` bytes in RGBA
order. The corresponding numeric value depends on host byte order:
`0xAABBGGRR` on little-endian systems and `0xRRGGBBAA` on big-endian systems.
NaNoPy performs that native packing only for numeric conversion of a `Color`.
Public properties, iteration, equality, representation, color-space conversion,
and arithmetic remain RGBA. This boundary conversion keeps both Python
semantics and rendered pixels correct on either architecture.

## Collision candidate selection

`get_close_pairs()` is a grid-based broad phase: it returns candidate pairs
whose grid cells are equal or adjacent in either axis. It does not perform an
exact distance calculation; callers should still apply their desired distance
test to each candidate.

For same-set (AA) matching, every unordered pair is yielded at most once. For
two-set (AB) matching, the first index belongs to A and the second to B.

The collision functions reject ambiguous or unsafe inputs:

- `gridsize` must be finite and greater than zero;
- x and y coordinate iterables for a set must have equal lengths;
- B x and y iterables must either both be provided or both be omitted.

One-shot iterables such as generators are supported.

### Applying a function to candidates

`apply_to_close_pairs()` is the decorator form of the same broad-phase query.
It runs the decorated callback immediately for every candidate pair when the
function definition is executed. The callback still needs an exact distance
or overlap check:

```python
from math import hypot

from NaNoPy import apply_to_close_pairs

xs = [0.0, 0.4, 10.0]
ys = [0.0, 0.3, 10.0]
maximum_distance = 1.0


@apply_to_close_pairs(xs, ys, gridsize=maximum_distance)
def handle_candidate(i: int, j: int) -> None:
    if hypot(xs[i] - xs[j], ys[i] - ys[j]) <= maximum_distance:
        print(f"particles {i} and {j} overlap")
```

The original callback is returned after this eager pass, so it can still be
called directly. For AB matching, pass `xs_b=` and `ys_b=` by keyword; the
callback receives the A index first and the B index second.

## Keyboard input

`KeyListener` callbacks always receive the triggering SDL event. A callback
that only needs to perform an action can ignore it explicitly:

```python
from NaNoPy.classes import KeyListener

listener = KeyListener()
listener.bind("space", lambda _event: print("space pressed"))
canvas.add_listener(listener)
```

Handlers that need event details use the same one-argument signature:

```python
from sdl2 import SDL_Event


def on_left(event: SDL_Event) -> None:
    print(event.key.keysym.sym, event.key.repeat)


listener.bind("left", on_press=on_left)
```

Each binding can provide an `on_press` callback, an `on_release` callback, or
both. `KeyListener.bind_many()` accepts a mapping when several keys share the
same setup code.

## Recording dimensions and FFmpeg arguments

The first captured frame fixes a recording's dimensions. Video streams require
a stable frame size, so resizing the canvas during an active recording causes
the next capture to raise `ValueError` before the differently sized frame is
written. Resize back to the original dimensions to continue, or stop and start
a new recording for the new size.

`fps` must be a positive integer and codec names are restricted to ordinary
FFmpeg encoder-name characters. Paths are passed to FFmpeg as individual
process arguments with shell execution disabled, so spaces and shell
punctuation in a file name are not executed as commands.

## Drawing coordinates

Every public `Writer` primitive uses Cartesian canvas coordinates:

- `(0, 0)` is the bottom-left pixel;
- increasing x moves right;
- increasing y moves up;
- the top row of a canvas with height `h` is `y = h - 1`.

SDL uses a top-left origin, so NaNoPy converts y at the rendering boundary:

```text
sdl_y = canvas_height - 1 - public_y
```

Coordinates are converted to integers but are not clipped. Custom polygons
use this same coordinate system and accept integer or floating-point point
coordinates. Stars, regular polygons, and custom polygons require at least
three points/sides.

Rectangles, circles, stars, polygons, and closed splines accept a keyword-only
`fill_color`. Supplying it requests a fill even if `filled` remains `False` and
draws `color` as a separate outline. Use `filled=True` without `fill_color` for
the original single-color fill behavior. A spline must also have `loop=True`
before either fill option has an effect.

### Migration note

Older releases used `canvas_height - y`. That placed public `y = 0` one row
outside the canvas and shifted all visible primitives by one pixel. Correct
code should use the documented public range `0 <= y < canvas_height`; no
manual y offset or pre-inversion is necessary for custom polygons.
