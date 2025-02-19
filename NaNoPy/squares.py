from __init__ import *

xSize = 800
ySize = 400


screen = canvas("screen1",xSize,ySize,xpos=50,ypos=50)
pen = pen(screen)

#help(canvas)
#help(pen)
help(color)

pen.drawRectangle(50,50,50,50,color().green,False)
pen.drawRectangle(100,50,50,50,color()(r=0,g=255,a=150),True)
pen.drawRectangle(151,50,50,50,color()(r=0,g=255,a=100),True)
pen.drawRectangle(202,50,50,50,color()(r=0,g=255,a=50),True)
screen.update()
screen.keepwindow()