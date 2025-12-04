from sdl2.ext import Color as Colorsdl2

class Color:
    """Color object for nanopy shapes
    
    Available colors: red, blue, green, yellow, magenta, cyan, white, gray

    Usage example Color().red

    For custom colors use Color()(r=<r>,g=<g>,b=<b>,a=<a>) 
    <r>, <g> and <b> are colors between 0 and 255
    <a> is the alpha (opacity) between 0 and 255

    """

    def __init__(self):
        self.red = Colorsdl2(255,0,0,255)
        self.blue = Colorsdl2(255, 255, 0, 0)
        self.green = Colorsdl2(255, 0, 255,0 )
        self.yellow = Colorsdl2(255, 0, 255, 255)
        self.magenta = Colorsdl2(255, 255, 0, 255)
        self.cyan = Colorsdl2(255, 255, 255,0 )
        self.white = Colorsdl2(255,255,255,255)
        self.gray = Colorsdl2(255,155,155,155)

    def __call__(self,*,r=255,g=0,b=0,a=255):
        return Colorsdl2(a,b,g,r)