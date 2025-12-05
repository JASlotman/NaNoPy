from NaNoPy import Canvas, Writer, Color
import random

def demo(hundreds: int = 2) -> None:
    # Create the drawing window and basic tools
    x_size = 800
    y_size = 600
    screen = Canvas(f"{100*hundreds} Dots Animation", x_size, y_size)
    pen = Writer(screen)
    screen.clear()
    
    # Emit dots with a short delay between each frame
    for _ in range(100 * hundreds):
        # Pick a random in-bounds position so dots stay away from the border
        x = random.randint(50, x_size-50)
        y = random.randint(50, y_size-50)
        
        # Generate a random cool-toned color for variety
        dot_color = Color.custom( 
            g = random.randint(100, 255), 
            b = random.randint(100, 255)
        )
        
        # Draw the dot at the chosen location
        pen.draw_circle(x, y, 5, dot_color, True)
        
        
        # Refresh the canvas to show the new dot
        screen.update()
        
        # Pause briefly to create an animation effect
        screen.pause(100)
    
    # Keep the window open once the animation finishes
    screen.keepwindow()

# Run the demo when executed directly
if __name__ == "__main__":
    demo(2)