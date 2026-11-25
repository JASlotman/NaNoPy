from sdl2 import SDL_RENDERER_ACCELERATED, SDL_RENDERER_PRESENTVSYNC, SDL_RENDERER_TARGETTEXTURE

ARGB_MASK = [0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000]

RENDER_FLAGS = SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC | SDL_RENDERER_TARGETTEXTURE
DEFAULT_CODEC = "libx265"  # H.265 codec for better compression

# zlib compression levels for PNG output (notebook display, ``Frame.to_png``).
# Any integer from PNG_LEVEL_MIN to PNG_LEVEL_MAX is accepted; these presets name
# the common trade-offs. Lower levels encode faster, higher levels write smaller files.
PNG_LEVEL_MIN = 0  # no compression at all: fastest, largest
PNG_LEVEL_FAST = 1  # live notebook animation, where encode time is the bottleneck
PNG_LEVEL_BALANCED = 6  # zlib's own default
PNG_LEVEL_SMALL = 9  # exported or shared images, where file size matters more than time
PNG_LEVEL_MAX = 9
DEFAULT_PNG_LEVEL = PNG_LEVEL_FAST
