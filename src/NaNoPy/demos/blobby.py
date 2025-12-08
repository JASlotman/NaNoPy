from NaNoPy import canvas, writer, color
import random as rnd
import math

xSize = 800
ySize = 600

screen = canvas("blob", xSize, ySize)
pen = writer(screen)

x = []
y = []
r = []
a = []

xc = xSize / 2
yc = ySize / 2

n = 7
npart = 5

xpart = []
ypart = []

for i in range(npart):
    xpart.append(xc)
    ypart.append(yc)

for i in range(n):
    r.append(rnd.randint(100, 120))
    a.append(((2 * math.pi) / n) * i)
    x.append(xc + (math.cos(a[i]) * r[i]))
    y.append(yc + (math.sin(a[i]) * r[i]))


while screen.running():
    for i in range(n):
        dr = rnd.randint(-5, 5)
        if r[i] + dr > 50 and r[i] + dr < 250:
            # r[i] += dr
            pass
        x[i] = xc + (math.cos(a[i]) * r[i])
        y[i] = yc + (math.sin(a[i]) * r[i])

    # pen.drawSpline(x,y,color.yellow,True,filled=True)
    pen.drawSpline(x, y, color.magenta, True, filled=False)

    for i in range(npart):
        dx = rnd.randint(-5, 5)
        dy = rnd.randint(-5, 5)

        if pen.spln.get_inside(xpart[i] + dx, ypart[i] + dy):
            xpart[i] += dx
            ypart[i] += dy

    for i in range(npart):
        pen.drawCircle(xpart[i], ypart[i], 5, color.magenta, True)

    screen.update()
    screen.pause(12)
    screen.clear()
