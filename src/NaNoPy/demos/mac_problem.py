from NaNoPy import *

xSize = 800
ySize = 500

screen = canvas("this shows the mac problem", xSize, ySize)
pen = writer(screen)

pen.draw_line(10, 150, 710, 490, color().red)
pen.draw_circle(600, 290, 5, color().green, True)
screen.update()
screen.keepwindow()