from views.battle_view import BattleView
from models.battle_model import BattleModel
import pygame
import pygame.gfxdraw
import math
import re

"""
TODO
- Raccourcir la fonction de load des sprites
- Resoudre le probleme de l'axe Z
- Ajouter archer et cavalier
"""

switchOrientation = {
    "(1, 1)": "front",
    "(-1, -1)": "back",
    "(0, 1)": "s-west",
    "(-1, 0)": "n-west",
    "(1, 0)": "s-east",
    "(0, -1)": "n-east",
    "(-1, 1)": "left",
    "(1, -1)": "right"
}

switchOrderConvert = {
    "Attack":"attack",
    "Wait":"stand",
    "Move":"walk"
}


def assetLoaderPikeman(unitname):
    assetLoaded = {
        "stand": {"front": [],
                  "back": [],
                  "s-west": [],
                  "n-west": [],
                  "s-east": [],
                  "n-east": [],
                  "left": [],
                  "right": []},
        "walk": {"front": [],
                  "back": [],
                  "s-west": [],
                  "n-west": [],
                  "s-east": [],
                  "n-east": [],
                  "left": [],
                  "right": []}
    }
    # raccourcir cette fonction avec un json pour les bitmaps
    # -STAND ANIMATION 9 * 5
    for i in range(1, 9):
        assetLoaded["stand"]["front"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["front"][i-1].set_colorkey((255, 0, 255))
    for i in range(9, 17):
        assetLoaded["stand"]["s-west"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["s-west"][i - 9].set_colorkey((255, 0, 255))
        assetLoaded["stand"]["s-east"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert(), True, False))
        assetLoaded["stand"]["s-east"][i - 9].set_colorkey((255, 0, 255))
    for i in range(17, 25):
        assetLoaded["stand"]["left"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["left"][i - 17].set_colorkey((255, 0, 255))
        assetLoaded["stand"]["right"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert(), True, False))
        assetLoaded["stand"]["right"][i - 17].set_colorkey((255, 0, 255))
    for i in range(25, 33):
        assetLoaded["stand"]["n-west"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["n-west"][i - 25].set_colorkey((255, 0, 255))
        assetLoaded["stand"]["n-east"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert(), True, False))
        assetLoaded["stand"]["n-east"][i - 25].set_colorkey((255, 0, 255))
    for i in range(33, 41):
        assetLoaded["stand"]["back"].append(pygame.image.load(
            "views/assets/units/pikeman/Stand Ground/{}stand{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["stand"]["back"][i - 33].set_colorkey((255, 0, 255))

    # -WALK ANIMATION 10 * 5
    for i in range(1, 11):
        print(i)
        assetLoaded["walk"]["front"].append(pygame.image.load(
            "views/assets/units/pikeman/walk/{}walk{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["walk"]["front"][i-1].set_colorkey((255, 0, 255))
    for i in range(11, 21):
        assetLoaded["walk"]["s-west"].append(pygame.image.load(
            "views/assets/units/pikeman/walk/{}walk{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["walk"]["s-west"][i - 11].set_colorkey((255, 0, 255))
        assetLoaded["walk"]["s-east"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/walk/{}walk{:003d}.bmp".format(unitname, i)).convert(), True, False))
        assetLoaded["walk"]["s-east"][i - 11].set_colorkey((255, 0, 255))
    for i in range(21, 31):
        assetLoaded["walk"]["left"].append(pygame.image.load(
            "views/assets/units/pikeman/walk/{}walk{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["walk"]["left"][i - 21].set_colorkey((255, 0, 255))
        assetLoaded["walk"]["right"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/walk/{}walk{:003d}.bmp".format(unitname, i)).convert(), True, False))
        assetLoaded["walk"]["right"][i - 21].set_colorkey((255, 0, 255))
    for i in range(31, 41):
        assetLoaded["walk"]["n-west"].append(pygame.image.load(
            "views/assets/units/pikeman/walk/{}walk{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["walk"]["n-west"][i - 31].set_colorkey((255, 0, 255))
        assetLoaded["walk"]["n-east"].append(pygame.transform.flip(pygame.image.load(
            "views/assets/units/pikeman/walk/{}walk{:003d}.bmp".format(unitname, i)).convert(), True, False))
        assetLoaded["walk"]["n-east"][i - 31].set_colorkey((255, 0, 255))
    for i in range(41, 51):
        assetLoaded["walk"]["back"].append(pygame.image.load(
            "views/assets/units/pikeman/walk/{}walk{:003d}.bmp".format(unitname, i)).convert())
        assetLoaded["walk"]["back"][i - 41].set_colorkey((255, 0, 255))
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
        self.action = switchOrderConvert[re.findall("[A-z]{3,}",str(unitData.action))[2]]
        self.TEXTURE = pygameSim.ASSETS_PIKEMAN
        self.pygameSim = pygameSim
        self.image = None
        self.rec = None
        self.direction = self.unitData.direction
        self.animation = "stand"
        self.animationKey = 0
        self.animationKeyMax = len(self.TEXTURE["stand"][switchOrientation[str(self.direction)]]) -1  #get animation max from TEXTURE
        self.is_alive = True
        """
        for u in switchOrientation.keys():
            print("Side : {} {}".format(u,len(self.TEXTURE["stand"][switchOrientation[str(self.direction)]])))
        """

    def update (self):
        self.x = self.unitData.x
        self.y = self.unitData.y
        self.direction = self.unitData.direction

        if self.is_alive != self.unitData.is_alive():
            self.is_alive = False
            self.animation = "dying"
            self.animationKeyMax = self.TEXTURE[self.action][switchOrientation[str(self.direction)]]
            self.animationKey = 1

        if switchOrderConvert[re.findall("[A-z]{3,}",str(self.unitData.action))[2]] != self.action and self.is_alive == True:
            self.action = switchOrderConvert[re.findall("[A-z]{3,}",str(self.unitData.action))[2]]
            self.animation = self.action
            self.animationKey = 1
            self.animationKeyMax = len(self.TEXTURE[self.action][switchOrientation[str(self.direction)]])-1
        elif self.animation == "dying":
            if self.animationKey < self.animationKeyMax: self.animationKey += 0.1
        else:
            if self.animationKey > self.animationKeyMax:
                self.animationKey = 0
            else:
                self.animationKey += 0.1

        try:
            self.image = self.TEXTURE[self.animation][switchOrientation[str(self.direction)]][math.floor(self.animationKey)]
        except IndexError:
            print("Index error : Side : {} Key : {:d}/{:d}".format(self.direction,math.floor(self.animationKey),self.animationKeyMax))
        self.rect = self.image.get_rect(midbottom=self.pygameSim.convertCartToIso((self.x, self.y)))

class PygameView(BattleView):
    def __init__(self, model : BattleModel, controller):
        super().__init__(model, controller)

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
        self.unit_spritegroup = pygame.sprite.Group()
        for unit in self.model.list_objects:
            tmp = unit_model(unit,self)
            self.object_list.append(tmp)
            self.unit_spritegroup.add(tmp)




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
        self.unit_spritegroup.update()
        self.unit_spritegroup.draw(self.map)
        self.window.blit(self.map, (0,0))
        pygame.display.flip()
        pygame.time.wait(1)

    def getInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
