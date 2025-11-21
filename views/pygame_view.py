from views.battle_view import BattleView
from models.battle_model import BattleModel
import pygame
import pygame.gfxdraw
import math


def assetLoaderPikeman(unitname):
    assetLoaded = {
        "stand": {"front": [],
                  "back": [],
                  "s-west": [],
                  "n-west": [],
                  "s-east": [],
                  "n-east": [],
                  "left": [],
                  "right": []}}
    # -STAND ANIMATION 9 * 5
    for i in range(1, 8):
        assetLoaded["stand"]["front"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["front"][i-1].set_colorkey((255, 0, 255))
    for i in range(9, 16):
        assetLoaded["stand"]["s-west"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["s-east"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert(), False, True))
    for i in range(17, 24):
        assetLoaded["stand"]["left"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["right"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert(), False, True))
    for i in range(25, 32):
        assetLoaded["stand"]["n-east"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["n-west"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert(), False, True))
    for i in range(33, 40):
        assetLoaded["stand"]["back"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
    # -WALK ANIMATION 10 * 5
    # -FIGHT ANIMATION 10 * 5
    # -DIE ANIMATION 10 * 5
    return assetLoaded

class unit_model(pygame.sprite.Sprite):
    def __init__(self,unitData,pygameSim):
        super().__init__()
        self.unitData = unitData
        self.x = unitData.x
        self.y = unitData.y
        self.name = unitData.name
        self.action = unitData.action
        self.TEXTURE = pygameSim.ASSETS_PIKEMAN
        self.pygameSim = pygameSim
        self.image = None
        self.rec = None
        self.animation = "stand"
        self.animationKey = 1
        self.animationKeyMax = 1 #get animation max from TEXTURE
        self.orientation = (0,0)
        self.is_alive = True
        self.swtich={
            '(0,0)':"front",
            '(0,0)': "back",
            '(0,0)': "s-west",
            '(0,0)': "n-west",
            '(0,0)': "s-east",
            '(0,0)': "n-east",
            '(0,0)': "left",
            '(0,0)': "right"
        }

    def update (self):
        self.x = self.unitData.x
        self.y = self.unitData.y
        self.orientation = self.unitData.orientation

        if self.is_alive != self.unitData.is_alive():
            self.is_alive = False
            self.animation = "dying"

            self.animationKeyMax = self.TEXTURE[self.action][self.swtich[self.orientation]]
            self.animationKey = 1

        if self.unitData.action != self.action and self.is_alive == True:
            self.action = self.unitData.action
                #change animation
            self.animationKey = 1
            self.animationKeyMax = self.TEXTURE[self.action][self.swtich[self.orientation]]
        elif self.animation == "dying":
            if self.animationKey < self.animationKeyMax: self.animationKey += 1
        else:
            if self.animationKey+1 > self.animationKeyMax:
                self.animationKey = 1
            else:
                self.animationKey = self.animationKey+1

        self.image = self.TEXTURE[self.action][swtich[self.orientation]](self.animationKey)
        self.rect = self.image.get_rect(midbottom=self.pygameSim(self.x, self.y))

class PygameView(BattleView):
    def __init__(self, model : BattleModel):
        super().__init__(model)

        #---MAP & WINDOW CONST---
        self.MAP_HEIGHT = model.map_height
        self.MAP_WIDTH = model.map_width
        self.MAP_DIAG = ((self.MAP_HEIGHT**2 + self.MAP_HEIGHT**2)**0.5)

        self.WINDOW_HEIGHT = 1000
        self.WINDOW_WIDTH = 1000
        self.WINDOW_OFFSET_H = self.WINDOW_HEIGHT / 2
        self.WINDOW_OFFSET_W = self.WINDOW_WIDTH / 2

        self.SCALE = 3

        #---PYGAME ENV DEFINE---
        pygame.init()
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

        #---MAP VARIABLES---
        self.MAP_TEXTURE = pygame.image.load('views/assets/grounds/map.png').convert()
        self.map = pygame.Surface((self.WINDOW_WIDTH*self.SCALE, self.WINDOW_HEIGHT*self.SCALE))
        self.map_x = 0
        self.map_y = 0

        #---Unit asset loading--
        #--PIKEMAN
        self.ASSETS_PIKEMAN = assetLoaderPikeman('Pikeman')
        self.object_list = []
        for unit in self.model.list_objects:
            self.object_list.append(unit_model(unit,self))




    def makeMap(self,pos_x,pos_y):
        """MAP constructor"""
        self.map.fill((0,0,0))
        points = [self.convertCartToIso((pos_x, pos_y)),
              self.convertCartToIso((pos_x+self.MAP_WIDTH, pos_y)),
              self.convertCartToIso((pos_x+self.MAP_WIDTH, pos_y+self.MAP_HEIGHT)),
              self.convertCartToIso((pos_x, pos_y+self.MAP_HEIGHT))]
        pygame.gfxdraw.textured_polygon(self.map, points, self.MAP_TEXTURE, 0, 0)

    def convertCartToIso(self,points):
        """Function to convert cartesian position to isometric position"""
        iso_x = math.floor(((points[0]-points[1])*self.SCALE)+(self.WINDOW_OFFSET_W-self.MAP_DIAG/4))
        iso_y = math.floor((((points[0]+points[1])/2)*self.SCALE)+(self.WINDOW_OFFSET_H-self.MAP_DIAG/2))
        #print("Unit cord x:{} y:{} iso cord x:{} y:{}".format(points[0],points[1],iso_x, iso_y))
        return [iso_x, iso_y]

    def render(self):
        self.getInput()
        self.window.fill((0,0,0))
        self.map.fill((0,0,0))
        self.makeMap(0,0)
        for unit in self.object_list:
            unit.update()
            self.map.blit(unit.image, unit.rec)
        self.window.blit(self.map, (0,0))
        pygame.display.flip()
        pygame.time.wait(1)

    def getInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
