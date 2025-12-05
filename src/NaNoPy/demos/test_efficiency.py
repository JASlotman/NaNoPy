import NaNoPy 
from NaNoPy import color
import random as rnd

# This is a test file for the NaNoPy library.
xSize = int(1920/2)
ySize = int(1080/2)
screen = NaNoPy.canvas("Zamkor", xSize, ySize)
pen = NaNoPy.writer(screen)
y = ySize / 2
stars=[]
particles = []  # List to store trailing particles

for i in range(500):
    stars.append((rnd.randint(0, xSize), rnd.randint(0, ySize)))
while screen.running():  
    for x in range(xSize):
        for i in range(len(stars)):
            pen.drawPixel(stars[i][0], stars[i][1], color().white)
            
        # Add new particles at the star's position
        for _ in range(5):  # Add 5 particles each frame
            particles.append([x, y, rnd.uniform(-1, 0), rnd.uniform(-0.5, .5), rnd.randint(5, 300)])  # [x, y, x_velocity, y_velocity, lifetime]
        
        # Update and draw particles
        i = 0
        while i < len(particles):
            particle = particles[i]
            # Update particle position
            particle[0] += particle[2]  # Update x position
            particle[1] += particle[3]  # Update y position
            particle[4] -= 1  # Decrease lifetime
            
            # Draw the particle
            pen.drawPixel(int(particle[0]), int(particle[1]), color().red)
            
            # Remove particles that have expired
            if particle[4] <= 0:
                particles.pop(i)
            else:
                i += 1
                
        # Draw the star
        pen.drawStar(x, y, 10,5, color().yellow,True)
        screen.update()
        screen.clear()
    screen.pause(20)
    screen.clear()
    screen.update()
    