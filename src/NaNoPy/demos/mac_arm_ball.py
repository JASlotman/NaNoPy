# apparently simple not looped operations are braking on macOS arm
# based on one of firs exercises (blue ball)
from NaNoPy import *
width = 800
height = 800

screen = canvas("circle", width, height)
pen = writer(screen)

pen.drawCircle(width/2, height/2, 50, color().blue, True)
screen.update() # The screen needs to be updated to see the effect of the clearing 


screen.pause(500) 
screen.clear() 
screen.update() # The screen needs to be updated to see the effect of the clearing 
screen.keepwindow()
