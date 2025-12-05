from NaNoPy import *

xSize = 800
ySize = 400

screen = canvas("screen1", xSize, ySize, xpos = 50, ypos = 50)
pen = writer(screen)

#help(canvas)
#help(pen)
#help(color)

pen.draw_rectangle(50, 50, 50, 50, Color.green, False)
pen.draw_rectangle(100, 50,50,50, Color.custom(r=0,g=255,a=150), True)
pen.draw_rectangle(151, 50, 50, 50, Color.custom(r=0,g=255,a=100), True)
pen.draw_rectangle(202, 50, 50, 50,Color.custom(r=0,g=255,a=50), True)
pen.draw_polygon(50, 150, 25, 4, Color.green, False)
pen.draw_polygon(100, 150, 25, 4, Color.custom(r=0,g=255,a=150), True)
pen.draw_polygon(151, 150, 25, 4, Color.custom(r=0,g=255,a=100), True)
pen.draw_polygon(202, 150, 25, 4, Color.custom(r=0,g=255,a=50), True)
pen.draw_polygon(50, 250, 25, 6, Color.green, False)
pen.draw_polygon(100, 250, 25, 6, Color.custom(r=0,g=255,a=150), True)
pen.draw_polygon(151, 250, 25, 6, Color.custom(r=0,g=255,a=100), True)
pen.draw_polygon(202, 250, 25, 6, Color.custom(r=0,g=255,a=50), True)

pen.draw_spline(
    [400, 500, 500, 400], 
    [200, 200,300, 300],
    Color.red,
    True,
    True
    )

pen.draw_circle(400, 200, 5, Color.red, True)
pen.draw_circle(400, 300, 5, Color.red, True)
pen.draw_circle(500, 300, 5, Color.red, True)
pen.draw_circle(500, 200, 5, Color.red, True)

screen.update()
screen.keep_window()