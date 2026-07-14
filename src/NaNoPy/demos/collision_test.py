from NaNoPy import Canvas, Writer, Color, apply_to_close_pairs
import math

screen = Canvas("test",800,600)
pen = Writer(screen)

x = []
y = []
bound = []

x2 = []
y2 = []
bound2 = []


#distances 15 25 35 45

for i in range(5):
    for j in range(5):
        x.append(100+((i*5)*i)+(i*10))
        y.append(100+((j*5)*j)+(j*10))
        bound.append(False)

        x2.append(400+((i*5)*i)+(i*10))
        y2.append(100+((j*5)*j)+(j*10))
        bound2.append(False)


def collision_test():

    maxdist = 25

    @apply_to_close_pairs(x,y,math.ceil(maxdist * 2))
    def collision(i,j):
        if i != j:
            if math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2 ) <= maxdist:
                bound[i] = True
                bound[j] = True
        #print("singe",i,j)

    @apply_to_close_pairs(x2,y2,math.ceil(maxdist * 2), x2s = x2, y2s = y2)
    def collision_dual(i,j):
        if i != j:
            if math.sqrt(((x2[i]-x2[j])**2) + ((y2[i]-y2[j])**2)) <= maxdist:
                bound2[i] = True
                bound2[j] = True
        #print("dual",i,j)

    for i in range(len(x)):
        if bound[i]:
            col = Color.red
        else:
            col = Color.black

        #pen.draw_string(x[i],y[i],Color.white,str(x[i]))
        pen.draw_circle(x[i],y[i],3,col,True)
        pen.draw_circle(x[i],y[i],3,Color.green,False)
        

        if bound2[i]:
            col = Color.red
        else:
            col = Color.black

        #pen.draw_string(x2[i],y2[i],Color.white,str(i))
        pen.draw_circle(x2[i],y2[i],3,col,True)
        pen.draw_circle(x2[i],y2[i],3,Color.green,False)
        
    
    screen.update()
    screen.keep_window()

if __name__ == "__main__":
    collision_test()