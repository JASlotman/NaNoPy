from NaNoPy import Canvas, Writer, Color, Collision
import math
import random as rnd

def demo():
    xsize = 800
    ysize = 600
    screen = Canvas("test",xsize,ysize)
    pen = Writer(screen)

    x = []
    y = []
    bound = []
    boundto = [] 

    n = 2000

    type = 0 # 0: new collision method, 1: old collsision method

    for i in range(n):
        x.append(rnd.randint(0,xsize))
        y.append(rnd.randint(0,ysize))
        bound.append(False)
        boundto.append(-1)

    while screen.running():
        

        for i in range(n):
            dx = rnd.randint(-4,4)
            dy = rnd.randint(-4,4)

            if x[i]+dx > 0 and x[i]+dx < xsize and y[i]+dy > 0 and y[i] + dy < ysize and not bound[i]:
                x[i] += dx
                y[i] += dy
        
        

        maxdist = 5
        #data = create_dictionary(x,y,maxdist*1.5,xsize,ysize)
        if type==0:
            
            
            
            @screen.collision.loop(x,y,x,y,maxdist*1.5)
            def func(i,j):
                dist = math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2)
                if dist < maxdist and not bound[i] and not bound[j] and i != j:
                    bound[i] = True
                    bound[j] = True
        if type==1:
            for i in range(n):
                for j in range(n):
                    dist = math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2)
                    if dist < maxdist and not bound[i] and not bound[j] and i != j:
                        bound[i] = True
                        bound[j] = True
                

        for i in range(n):
            if rnd.random() < 0.05:
                bound[i] = False
                boundto[i] = False
                
        for i in range(n):
            if bound[i]:
                col = Color.red
            else:
                col = Color.green
            
            pen.draw_circle(x[i],y[i],3,col,True)
        
        screen.update()
        screen.pause(0)
        screen.clear()

if __name__ == "__main__":
    demo()