#simple test
from __init__ import *

xSize = 800
ySize = 400


screen = canvas("screen1",xSize,ySize,xpos=50,ypos=50)
screen2 = canvas("screen2",xSize,ySize,xpos=50+xSize,ypos=50)
pen1 = pen(screen)
pen2 = pen(screen2)


while screen.running():
    pen1.drawCircle(100,100,60,color().green,True)
    pen1.drawString(100,100,color().red,"Hello")
    pen1.drawLine(0,200,800,200,color().green)
    screen.update()
    screen.pause(500)
    screen.clear()
    screen.update()
    screen.pause(500)
    pen2.drawCircle(100, 100, 60, color().green, True)
    pen2.drawString(100,100, color()(r=255,g=255,b=255),"World")
    screen2.update()
    screen2.pause(500)
    screen2.clear()
    screen2.update()
    screen2.pause(500)

