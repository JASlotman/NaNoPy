from time import sleep

from NaNoPy import canvas, writer

screen = canvas("title", 200, 200)
pen = writer(screen)

pen.draw_circle(50, 50, 10)

screen.update()

sleep(3)
