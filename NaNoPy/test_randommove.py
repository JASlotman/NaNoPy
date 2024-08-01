from NaNoPy import *
import random

xSize = 800
ySize = 400

screen = canvas("Name",xSize,ySize)
pen = pen(screen)

n = 10
x = list()
y = list()

for i in range(n):
    x.append(random.randint(0,xSize))
    y.append(random.randint(0,ySize))

frame = 1

while screen.running():
    frame += 1
    for i in range(n):
        dx = random.randint(-4,4)
        dy = random.randint(-4,4)
        if x[i] + dx > 0 and x[i] + dx < xSize and y[i] + dy > 0 and y[i] + dy < ySize:
            x[i] += dx
            y[i] += dy

    for i in range(n):
        pen.drawCircle(x[i],y[i],5,color().green,True)
        pen.drawString(x[i], y[i], color().red,"f:" + str(frame) + " p: " + str(i) + " x:" + str(x[i]) + " y:" + str(y[i]))
        pen.drawLine(0,y[i],800,y[i],color().red,True)

    screen.update()
    screen.pause(50)
    screen.clear()

