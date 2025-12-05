from NaNoPy import *
import random

def draw_hundred_dots():
    # Utwórz okno
    xSize = 800
    ySize = 600
    screen = canvas("100 Dots Animation", xSize, ySize)
    pen = writer(screen)
    screen.clear()
    
    # Rysuj 100 kropek z opóźnieniem
    for i in range(100):
        # Losowa pozycja dla kropki
        x = random.randint(50, xSize-50)
        y = random.randint(50, ySize-50)
        
        # Losowy kolor (dla urozmaicenia)
        dot_color = color()(
            r=random.randint(100, 255), 
            g=random.randint(100, 255), 
            b=random.randint(100, 255)
        )
        
        # Rysowanie kropki
        pen.drawCircle(x, y, 5, dot_color, True)
        
        
        # Aktualizacja ekranu
        screen.update()
        
        # Pauza 100 ms
        screen.pause(100)
    
    # Utrzymaj okno otwarte po narysowaniu wszystkich kropek
    screen.keepwindow()

# Uruchom funkcję
if __name__ == "__main__":
    draw_hundred_dots()