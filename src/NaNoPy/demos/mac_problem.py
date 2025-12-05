from NaNoPy import Canvas, Writer, Color

x_size = 800
y_size = 500

screen = Canvas("this shows the mac problem", x_size, y_size)
pen = Writer(screen)

pen.draw_line(10, 150, 710, 490, Color.red)
pen.draw_circle(600, 290, 5, Color.green, True)
screen.update()
screen.keep_window()