from sdl2 import *
from sdl2.sdlgfx import *
from sdl2.ext import *
import ctypes
import sys


def canvas(xSize, ySize):
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"test", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, xSize, ySize, SDL_WINDOW_SHOWN)
    return window


def pencil(window):
    render_flags = (
            SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
    )

    pen = SDL_CreateRenderer(window, -1, render_flags)
    return pen


def drawcircle(pen, x, y, r, color):
    filledCircleColor(pen, int(x), int(y), r, color)


def update(window):
    ren = SDL_GetRenderer(window)
    SDL_RenderPresent(ren)


def clear(window):
    ren = SDL_GetRenderer(window)
    SDL_SetRenderDrawColor(ren, 0, 0, 0, 255)
    SDL_RenderClear(ren)


def pause(time):
    SDL_Delay(time)


def main():
    xsize = 600
    ysize = 400
    red = Color(255, 0, 0)
    screen = canvas(xsize, ysize)
    pen = pencil(screen)


    running = True
    event = SDL_Event()
    while running:

        drawcircle(pen, xsize/2, ysize/2, 4, red)

        update(screen)
        pause(12)
        #clear(screen)

        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break

    SDL_DestroyWindow(screen)
    SDL_Quit()

    return 0






if __name__ == "__main__":
    sys.exit(main())
