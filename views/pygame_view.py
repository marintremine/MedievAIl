from views.battle_view import BattleView
from models.battle_model import BattleModel
import pygame
import pygame.gfxdraw


class PygameView(BattleView):
    def __init__(self, model : BattleModel):
        super().__init__(model)

        #---MAP & WINDOW CONST---
        self.MAP_HEIGHT = model.map_height
        self.MAP_WIDTH = model.map_width

        self.WINDOW_HEIGHT = 800
        self.WINDOW_WIDTH = 1000
        self.WINDOW_OFFSET_H = self.WINDOW_HEIGHT / 2
        self.WINDOW_OFFSET_W = self.WINDOW_WIDTH / 2

        self.TILE_SIZE_H = 0
        self.TILE_SIZE_W = 0

        #---PYGAME ENV DEFINE---
        pygame.init()
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

        #---MAP VARIABLES---
        self.MAP_TEXTURE = pygame.image.load('views/assets/grounds/map.png').convert()
        self.map = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.map_x = 0
        self.map_y = 0

    def makeMap(self,pos_x,pos_y):
        """MAP constructor"""
        self.map.fill((0,0,0))
        points = [self.convertCartToIso((pos_x, pos_y)),
              self.convertCartToIso((pos_x+self.MAP_WIDTH, pos_y)),
              self.convertCartToIso((pos_x+self.MAP_WIDTH, pos_y+self.MAP_HEIGHT)),
              self.convertCartToIso((pos_x, pos_y+self.MAP_HEIGHT)),]
        pygame.gfxdraw.textured_polygon(self.map, points, self.MAP_TEXTURE, 0, 0)

    def convertCartToIso(self,points):
        """Function to convert cartesian position to isometric position"""
        iso_x = (points[0]-points[1]) + self.WINDOW_OFFSET_W
        iso_y = ((points[0]+points[1])/2) + (self.WINDOW_OFFSET_H - self.MAP_HEIGHT/2)
        return [iso_x, iso_y]

    def render(self):
        self.getInput()
        self.window.fill((0,0,0))
        self.makeMap(0,0)
        self.window.blit(self.map, (0,0))

        pygame.display.flip()

    def getInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()