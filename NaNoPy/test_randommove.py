from NaNoPy import *
import random

xSize = 800
ySize = 400

screen = canvas("Name",xSize,ySize)
pen = pen(screen)

n = 100
x = list()
y = list()

for i in range(n):
    x.append(random.randint(0,xSize))
    y.append(random.randint(0,ySize))

while screen.running():
    for i in range(n):
        dx = random.randint(-4,4)
        dy = random.randint(-4,4)
        if x[i] + dx > 0 and x[i] + dx < xSize and y[i] + dy > 0 and y[i] + dy < ySize:
            x[i] += dx
            y[i] += dy

    for i in range(n):
        pen.drawCircle(x[i],y[i],5,color().green,True)

    screen.update()
    screen.pause(12)
    screen.clear()

