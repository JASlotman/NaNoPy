#simple test
from NaNoPy import *

xSize = 800
ySize = 400


screen = canvas("screen1",xSize,ySize,xpos=50,ypos=50)
screen2 = canvas("screen2",xSize,ySize,xpos=50+xSize,ypos=50)
pen1 = pen(screen)
pen2 = pen(screen2)


while screen.running():
    pen1.drawCircle(100,100,20,color().green,True)
    screen.update()
    screen.pause(500)
    screen.clear()
    screen.update()
    screen.pause(500)
    pen2.drawCircle(100, 100, 20, color().green, True)
    screen2.update()
    screen2.pause(500)
    screen2.clear()
    screen2.update()
    screen2.pause(500)

