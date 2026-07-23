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

### Migration note

Older releases used `canvas_height - y`. That placed public `y = 0` one row
outside the canvas and shifted all visible primitives by one pixel. Correct
code should use the documented public range `0 <= y < canvas_height`; no
manual y offset or pre-inversion is necessary for custom polygons.
