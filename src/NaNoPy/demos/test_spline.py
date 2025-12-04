import numpy as np
from NaNoPy import *
import random as rnd

xSize = 800
ySize = 400

screen = canvas("screen1", xSize, ySize, xpos=50, ypos=50)
pen = writer(screen)

x = []
y = []
rad = []

xpart = []
ypart = []
radius = 5

n = 9
npart = 100

# for i in range(n):
    
#     xtemp = rnd.randint(0,xSize)
#     ytemp = rnd.randint(0,ySize)

#     while math.sqrt((xSize/2 - xtemp)**2 + (ySize/2 - ytemp)**2 ) > 53 or math.sqrt((xSize/2 - xtemp)**2 + (ySize/2 - ytemp)**2 ) < 50:
#         xtemp = rnd.randint(0,xSize)
#         ytemp = rnd.randint(0,ySize)
    
#     x.append(xtemp)
#     y.append(ytemp)
#     rad.append(math.atan2((ySize/2)-ytemp,(xSize/2)-xtemp))

# inds = np.array(rad).argsort()
# x = np.array(x)[inds]
# y = np.array(y)[inds]

for i in range(n):
    x.append((i* (xSize/(n-1))))
    y.append(ySize/2)

for i in range(npart):
    xpart.append(rnd.randint(radius, xSize-radius))
    ypart.append(ySize/2 + rnd.randint(-3,3))

print(x)

first = True

while screen.running():
    for i in range(0,len(x)):
        
        dy = rnd.randint(-3,3)

        #if 50 < math.sqrt((xSize/2 - (x[i]+dx))**2 + (ySize/2 - (y[i]+dy))**2 ) < 53:
        #x[i] += dx
        if  0 < i < len(x)-1:
            y[i] += dy
        #rad[i] = math.atan2((ySize/2)-y[i],(xSize/2)-x[i])

    # inds = np.array(rad).argsort()
    # x = np.array(x)[inds]
    # y = np.array(y)[inds]    
    if not first:
        splinedy = pen.spln.spliney

    pen.drawSpline(x,np.array(y)-50,color().green,False,False)
    pen.drawSpline(x,np.array(y)+50,color().green,False,False)

    if not first:
        
        spsize = min(pen.spln.spliney.size, splinedy.size)
        splinedy = pen.spln.spliney[0:spsize] - splinedy[0:spsize]
    
    if first:
        splinedy = np.zeros(pen.spln.spliney.size)

    first = False
    

    for i in range(npart):
        dx = rnd.randint(-5,5)
        dy = rnd.randint(-5,5)

        ind = np.where(pen.spln.splinex >= xpart[i])[0][0]

        
        ypart[i] += splinedy[ind%splinedy.size]
        
        if ypart[i]+dy < pen.spln.spliney[ind]-(2*radius) and ypart[i]+dy > (pen.spln.spliney[ind]-100)+(2*radius) and xpart[i]+dx > 0:
            xpart[i] += dx
            ypart[i] += dy 
            

        #flow
        flowdx = 5
        ind2 = np.where(pen.spln.splinex >= (xpart[i]+flowdx)%xSize)[0][0]
        flowdy =  pen.spln.spliney[ind2] - pen.spln.spliney[(ind)%pen.spln.splinex.size] 

        
        xpart[i] += flowdx
        ypart[i] += flowdy

        xpart[i] = xpart[i]%xSize

    for i in range(npart):
        pen.drawCircle(xpart[i],ypart[i],radius,color().red,True)
        pen.drawCircle(xpart[i],ypart[i],radius-3,color().yellow,True)


    # for i in range(len(x)):
    #     pen.drawCircle(x[i],y[i],3,color().yellow,False)
    #     pen.drawString(x[i],y[i],color().white,str(i))
    
    screen.update()
    screen.pause(12)
    screen.clear()



# n=10
# #print(np.diag(np.full(n-1,1),-1))
# matrix = np.diag(np.full(n-1,1),-1) + np.diag(np.full(n-1,1),+1) + np.diag(np.full(n,4),0)
# matrix[0,n-1] = 1
# matrix[n-1,0] = 1
# print(matrix)
# print(np.linalg.inv(matrix))
# print(np.matmul(np.linalg.inv(matrix),matrix))

# matrix2 = np.diag(np.full(n-1,1),-1) + np.diag(np.full(n-1,1),+1) + np.diag(np.full(n,4),0)
# matrix2[0,0] = 2
# matrix2[n-1,n-1] = 2

# print(matrix2)

# arr = np.arange(10)
# print(arr)
# arr1 = np.roll(arr,1,0)
# print(arr1)
# arr2 = np.roll(arr,-1,0)
# print(arr2)
# arr = arr1-arr2
# print(arr)

# t = np.linspace(0,1,25)
# v = np.arange(25)

# print(t)

# result = t + t*v + t*(v**2)
# print(result)



