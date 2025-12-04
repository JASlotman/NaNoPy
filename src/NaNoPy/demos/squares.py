from NaNoPy import *

xSize = 800
ySize = 400

screen = canvas("screen1", xSize, ySize, xpos = 50, ypos = 50)
pen = writer(screen)

#help(canvas)
#help(pen)
#help(color)

pen.drawRectangle(50, 50, 50, 50, color().green, False)
pen.drawRectangle(100, 50,50,50, color()(r=0,g=255,a=150), True)
pen.drawRectangle(151, 50, 50, 50, color()(r=0,g=255,a=100), True)
pen.drawRectangle(202, 50, 50, 50,color()(r=0,g=255,a=50), True)
pen.drawPolygon(50, 150, 25, 4, color().green, False)
pen.drawPolygon(100, 150, 25, 4, color()(r=0,g=255,a=150), True)
pen.drawPolygon(151, 150, 25, 4, color()(r=0,g=255,a=100), True)
pen.drawPolygon(202, 150, 25, 4, color()(r=0,g=255,a=50), True)
pen.drawPolygon(50, 250, 25, 6, color().green, False)
pen.drawPolygon(100, 250, 25, 6, color()(r=0,g=255,a=150), True)
pen.drawPolygon(151, 250, 25, 6, color()(r=0,g=255,a=100), True)
pen.drawPolygon(202, 250, 25, 6, color()(r=0,g=255,a=50), True)

pen.drawSpline(
    [400, 500, 500, 400], 
    [200, 200,300, 300],
    color().red,
    True,
    True
    )

pen.drawCircle(400, 200, 5, color().red, True)
pen.drawCircle(400, 300, 5, color().red, True)
pen.drawCircle(500, 300, 5, color().red, True)
pen.drawCircle(500, 200, 5, color().red, True)

screen.update()
screen.keepwindow()