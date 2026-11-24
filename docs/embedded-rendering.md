# Embedded rendering and PNG compression

`Canvas.update_embedded()` captures the canvas without presenting it and
returns a `Frame`: a read-only RGBA image backed by a numpy array. NaNoPy needs
no imaging library for this. Frames feed two things:

- **Notebook display.** Jupyter shows a `Frame` as a PNG, which NaNoPy encodes
  itself.
- **Video recording.** `MovieWriter.add_frame()` streams a frame's raw RGBA
  bytes to FFmpeg. No PNG is involved, so compression settings never affect
  recorded video.

## Choosing a compression level

PNG output uses zlib. The level (0-9) trades encode time against file size, and
the right choice depends on what the frames are for. The presets live in
`NaNoPy.constants`:

| Constant             | Level | Use it for                                                  |
| -------------------- | ----- | ----------------------------------------------------------- |
| `PNG_LEVEL_FAST`     | 1     | live notebook animation (the default)                       |
| `PNG_LEVEL_BALANCED` | 6     | a compromise, and zlib's own default                        |
| `PNG_LEVEL_SMALL`    | 9     | frames you save or share, where size matters more than time |

Any integer from `PNG_LEVEL_MIN` (0, no compression) to `PNG_LEVEL_MAX` (9) is
accepted. Out-of-range or non-integer values raise `ValueError` or `TypeError`.

For a 1920x1080 frame of flat shapes on a plain background, one run on a
development machine measured roughly:

| Level | Encode time | PNG size |
| ----- | ----------- | -------- |
| 1     | 1.2 ms      | 90 KB    |
| 6     | 2.5 ms      | 44 KB    |
| 9     | 15 ms       | 11 KB    |

Your numbers will differ with the machine and the picture. Noisy frames
compress poorly at every level, so there the level mostly costs time.

## Setting the level

```python
from NaNoPy.constants import PNG_LEVEL_SMALL

# For every frame a notebook loop displays:
@loop(frame_count=100, png_level=PNG_LEVEL_SMALL)
def draw(screen, pen, frame_index): ...

# For one capture:
frame = screen.update_embedded(png_level=PNG_LEVEL_SMALL)

# On a frame you already hold:
frame.png_level = PNG_LEVEL_SMALL   # used when the frame is displayed
png_bytes = frame.to_png(level=9)   # or choose per call
frame.save("frame.png", level=9)    # PNG only
```

With no level given, `DEFAULT_PNG_LEVEL` applies. A `loop()` that is not given
`png_level` leaves the level of any frame its callback returns untouched.

## Coming from Pillow

Earlier versions returned a Pillow image. `Frame` keeps `size`, `mode`
(always `"RGBA"`), `getpixel()`, `tobytes()` and `save()` (PNG only). If you
need other Pillow features, you can convert with
`PIL.Image.fromarray(frame.array)` after installing Pillow yourself.

A `@loop` callback should return `screen.update_embedded()`, `False` to stop,
or nothing. Any other object, including a Pillow image, is ignored: an embedded
loop captures the canvas itself.
