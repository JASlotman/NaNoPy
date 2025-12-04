from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDL_KEYUP

class Listener:
    def __init__(self, name:str):
        self.name = name
        
    def run(self, event) -> None:
        raise NotImplementedError("Extend Listener for Usability.")

    # def run(self,event):       
    #         if event.type == SDL_KEYDOWN:
    #             if event.key.keysym.sym == SDLK_RIGHT:
    #                 self.dx = 3
    #             elif event.key.keysym.sym == SDLK_LEFT:
    #                 self.dx = -3
    #         elif event.type == SDL_KEYUP:
    #              if event.key.keysym.sym in (SDLK_RIGHT,SDLK_LEFT):
    #                 self.dx = 0