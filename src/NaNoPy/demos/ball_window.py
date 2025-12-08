from NaNoPy import Canvas, Writer, Color
import math

def demo():
     x_size = 300
     y_size = 300

     screen = Canvas("Test", 300, 300)
     pencil = Writer(screen)
     color = Color.gray

     x_i, y_i = screen.get_window_pos()

     ball = {
          "x": x_i + x_size // 2,
          "y": y_i + y_size // 2,
          "dx": 0.,
          "dy": 0.
     }

     while screen.running():
          screen.clear()

          ball["dy"] = ball["dy"] + .98

          
          ball["x"] = ball["x"] + ball["dx"]
          ball["y"] = ball["y"] + ball["dy"]

          x, y = screen.get_window_pos()

          relative_x = ball["x"] - x
          relative_y = y_size - (ball["y"] - y)

          if relative_y <= 40:
               ball["dy"] = -1 * abs(ball["dy"])

               if relative_y > -20:
                    ball["y"] = y + y_size - 40

          if (relative_x < 0 or relative_x > x_size):
               theta = math.atan2(y_size // 2 - relative_y, x_size // 2 - relative_x)

               ball["dx"] += 0.1 * math.cos(theta)
          else:
               ball["dx"] *= .95

          pencil.draw_circle(ball["x"] - x, y_size - (ball["y"] - y), 40, color, True)

          screen.update()

if __name__ == "__main__":
    demo()
