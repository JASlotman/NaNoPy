from NaNoPy import *

xSize = 800
ySize = 500

screen = canvas("this shows the mac problem",xSize,ySize)
pen = writer(screen)

pen.drawLine(10,150,710,490,color().red)
pen.drawCircle(600,290,5,color().green,True)
screen.update()
screen.keepwindow()