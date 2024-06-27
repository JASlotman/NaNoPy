#simple test
from NaNoPy import *

xSize = 800
ySize = 400

screen = canvas(xSize,ySize)
pen = pen(screen)
while screen.running:
    pen.drawCircle(100,100,20,color().green,True)
    screen.update()
    screen.pause(50)
    screen.clear()
    screen.update()

screen.keepWindow()