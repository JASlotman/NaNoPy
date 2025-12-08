from NaNoPy import Canvas, Writer, Color
from typing import Any
import math
import colorsys

balls: list[dict[str, Any] ]= [{
     "x_size": 300,
     "y_size": 300,
     "x": 0,
     "y": 0,
     "dy": 0,
     "dx": 0
}, {
     "x_size": 300,
     "y_size": 300,
     "x": 0,
     "y": 0,
     "dy": 0,
     "dx": 0
}]

for i in range(len(balls)):
     ball = balls[i]
     ball["screen"] = Canvas(f"Ball {i}", ball["x_size"], ball["y_size"])
     ball["pen"] = Writer(ball["screen"])

     r, g, b = colorsys.hls_to_rgb((i / 20), .5, 1)

     x_i, y_i = ball["screen"].get_window_pos()

     ball["x"] = x_i + ball["x_size"] // 2
     ball["y"] = y_i + ball["y_size"] // 2
     ball["color"] = Color.custom(r=int(r * 255), g=int(g * 255), b=int(b * 255))

while any(map(lambda x: x["screen"].running(), balls)):
     for ball_renderer in balls:
          ball_renderer["screen"].clear()

          x, y = ball_renderer["screen"].get_window_pos()

          center_x = ball_renderer["x_size"] // 2
          center_y = ball_renderer["y_size"] // 2
          dx = center_x - (ball_renderer["x"] - x)
          dy = center_y - (ball_renderer["y"] - y)
          distance = (dx**2 + dy**2)**0.5
          theta = math.atan2(dy, dx)

          force = distance * .02

          ball_renderer["dx"] *= .9
          ball_renderer["dy"] *= .9

          ball_renderer["dx"] += math.cos(theta) * force
          ball_renderer["dy"] += math.sin(theta) * force


          ball_renderer["x"] += ball_renderer["dx"]
          ball_renderer["y"] += ball_renderer["dy"]


          for ball in balls:
               ball_renderer["pen"].draw_circle(ball["x"] - x, ball_renderer["y_size"] - (ball["y"] - y), 20, ball["color"], True)
          
          ball_renderer["screen"].update()