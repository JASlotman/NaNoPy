from NaNoPy import *
import random

def draw_hundreds_of_dots(hundreds: int) -> None:
    # Create the drawing window and basic tools
    xSize = 800
    ySize = 600
    screen = canvas(f"{100*hundreds} Dots Animation", xSize, ySize)
    pen = writer(screen)
    screen.clear()
    
    # Emit dots with a short delay between each frame
    for _ in range(100*hundreds):
        # Pick a random in-bounds position so dots stay away from the border
        x = random.randint(50, xSize-50)
        y = random.randint(50, ySize-50)
        
        # Generate a random cool-toned color for variety
        dot_color = Color.custom( 
            g=random.randint(100, 255), 
            b=random.randint(100, 255)
        )
        
        # Draw the dot at the chosen location
        pen.drawCircle(x, y, 5, dot_color, True)
        
        
        # Refresh the canvas to show the new dot
        screen.update()
        
        # Pause briefly to create an animation effect
        screen.pause(100)
    
    # Keep the window open once the animation finishes
    screen.keepwindow()

# Run the demo when executed directly
if __name__ == "__main__":
    draw_hundreds_of_dots(2)