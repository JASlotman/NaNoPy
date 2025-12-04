from sdl2.ext import Color

class color:
    """color object for nanopy shapes
    
    Available colors: red, blue, green, yellow, magenta, cyan, white, gray

    Usage example color().red

    For custom colors use color()(r=<r>,g=<g>,b=<b>,a=<a>) 
    <r>, <g> and <b> are colors between 0 and 255
    <a> is the alpha (opacity) between 0 and 255

    """

    def __init__(self):
        self.red = Color(255,0,0,255)
        self.blue = Color(255, 255, 0, 0)
        self.green = Color(255, 0, 255,0 )
        self.yellow = Color(255, 0, 255, 255)
        self.magenta = Color(255, 255, 0, 255)
        self.cyan = Color(255, 255, 255,0 )
        self.white = Color(255,255,255,255)
        self.gray = Color(255,155,155,155)


    def __call__(self,*,r=255,g=0,b=0,a=255):
        return Color(a,b,g,r)