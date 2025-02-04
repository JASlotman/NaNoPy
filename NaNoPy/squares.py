from __init__ import *

xSize = 800
ySize = 400


screen = canvas("screen1",xSize,ySize,xpos=50,ypos=50)
pen = pen(screen)

pen.drawRectangle(50,50,50,50,color().green,False)
screen.update()
screen.keepwindow()