from views.battle_view import BattleView
from models.battle_model import BattleModel
from settings import PYGAME_WIN
import pygame
import pygame.gfxdraw
import math
import json

"""
TODO
- Resoudre le probleme de l'axe Z
- Ajouter minimap
"""

LIST_UNITS = ["Pikeman","Crossbowman","Knight"]

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

def assetLoader(unitname):
    assetLoaded = {
        "attack": {"front": [],
                  "back": [],
                  "s-west": [],
                  "n-west": [],
                  "s-east": [],
                  "n-east": [],
                  "left": [],
                  "right": []
                   },
        "die": {"front": [],
                  "back": [],
                  "s-west": [],
                  "n-west": [],
                  "s-east": [],
                  "n-east": [],
                  "left": [],
                  "right": []
                },
        "stand": {"front": [],
                 "back": [],
                 "s-west": [],
                 "n-west": [],
                 "s-east": [],
                 "n-east": [],
                 "left": [],
                 "right": []
                  },
        "walk": {"front": [],
                 "back": [],
                 "s-west": [],
                 "n-west": [],
                 "s-east": [],
                 "n-east": [],
                 "left": [],
                 "right": []
                 }
    }

    with open("views/assets/units/{}/{}.json".format(unitname,unitname),"r", encoding="utf-8") as file:
        unit_json_map = json.load(file)

    for anim in assetLoaded:
        path = "views/assets/units/{}/{}/{}{}".format(unitname,anim, unitname,anim)

        for i in range(unit_json_map[anim]["side"]["front"]["start"],unit_json_map[anim]["side"]["front"]["end"]):
            assetLoaded[anim]["front"].append(pygame.image.load(
                "{}{:003d}.bmp".format(path,i)).convert())
            assetLoaded[anim]["front"][i-unit_json_map[anim]["side"]["front"]["start"]].set_colorkey((255, 0, 255))

        for i in range(unit_json_map[anim]["side"]["s-west"]["start"],unit_json_map[anim]["side"]["s-west"]["end"]):
            assetLoaded[anim]["s-west"].append(pygame.image.load(
                "{}{:003d}.bmp".format(path,i)).convert())
            assetLoaded[anim]["s-west"][i - unit_json_map[anim]["side"]["s-west"]["start"]].set_colorkey((255, 0, 255))

            assetLoaded[anim]["s-east"].append(pygame.transform.flip(pygame.image.load(
                "{}{:003d}.bmp".format(path,i)).convert(), True, False))
            assetLoaded[anim]["s-east"][i - unit_json_map[anim]["side"]["s-west"]["start"]].set_colorkey((255, 0, 255))
        for i in range(unit_json_map[anim]["side"]["left"]["start"],unit_json_map[anim]["side"]["left"]["end"]):
            assetLoaded[anim]["left"].append(pygame.image.load(
                "{}{:003d}.bmp".format(path,i)).convert())
            assetLoaded[anim]["left"][i - unit_json_map[anim]["side"]["left"]["start"]].set_colorkey((255, 0, 255))

            assetLoaded[anim]["right"].append(pygame.transform.flip(pygame.image.load(
                "{}{:003d}.bmp".format(path,i)).convert(), True, False))
            assetLoaded[anim]["right"][i - unit_json_map[anim]["side"]["left"]["start"]].set_colorkey((255, 0, 255))
        for i in range(unit_json_map[anim]["side"]["n-west"]["start"],unit_json_map[anim]["side"]["n-west"]["end"]):
            assetLoaded[anim]["n-west"].append(pygame.image.load(
                "{}{:003d}.bmp".format(path,i)).convert())
            assetLoaded[anim]["n-west"][i - unit_json_map[anim]["side"]["n-west"]["start"]].set_colorkey((255, 0, 255))

            assetLoaded[anim]["n-east"].append(pygame.transform.flip(pygame.image.load(
                "{}{:003d}.bmp".format(path,i)).convert(), True, False))
            assetLoaded[anim]["n-east"][i - unit_json_map[anim]["side"]["n-west"]["start"]].set_colorkey((255, 0, 255))
        for i in range(unit_json_map[anim]["side"]["back"]["start"],unit_json_map[anim]["side"]["back"]["end"]):
            assetLoaded[anim]["back"].append(pygame.image.load(
                "{}{:003d}.bmp".format(path,i)).convert())
            assetLoaded[anim]["back"][i - unit_json_map[anim]["side"]["back"]["start"]].set_colorkey((255, 0, 255))
    return assetLoaded


class unit_model(pygame.sprite.Sprite):
    def __init__(self,unitData,pygameSim,color):
        super().__init__()
        self.unitData = unitData
        self.x = unitData.x
        self.y = unitData.y
        self.color = color
        self.name = unitData.name
        self.action = unitData.currentAction
        self.TEXTURE = pygameSim.ASSETS[self.name]
        self.pygameSim = pygameSim
        self.image = None
        self.rec = None
        self.direction = self.unitData.direction
        self.animation = "stand"
        self.animationKey = 0
        self.animationKeyMax = len(self.TEXTURE["stand"][switchOrientation[str(self.direction)]]) -1
        self.is_alive = True
        self.displayText = self.pygameSim.font.render(str(self.unitData.general.name), False, color)

    def update (self):
        self.x = self.unitData.x
        self.y = self.unitData.y
        self.direction = self.unitData.direction

        # Play the dying animation
        if self.is_alive != self.unitData.is_alive():
            self.is_alive = False
            self.animation = "die"
            self.animationKeyMax = len(self.TEXTURE[self.animation][switchOrientation[str(self.direction)]])-1
            self.animationKey = 0

        # Play or actuate the actual animation
        if self.pygameSim.model.running == True:
            if self.unitData.currentAction != self.action and self.is_alive == True:
                self.action = self.unitData.currentAction
                self.animation = self.action
                self.animationKey = 0
                self.animationKeyMax = len(self.TEXTURE[self.action][switchOrientation[str(self.direction)]])-1

            elif self.animation == "die":
                if self.animationKey < self.animationKeyMax: self.animationKey += 0.1
            else:
                if self.animationKey > self.animationKeyMax:
                    self.animationKey = 0
                else:
                    self.animationKey += 0.1

        #Create the textured polygon for the map
        try:
            self.image = self.TEXTURE[self.animation][switchOrientation[str(self.direction)]][math.floor(self.animationKey)]
            self.image = pygame.transform.scale(
                self.image,
            ((self.image.get_width()/self.pygameSim.SCALE)*self.pygameSim.ZOOM,
                 (self.image.get_height()/self.pygameSim.SCALE)*self.pygameSim.ZOOM)
            )
            textTmp = pygame.PixelArray(self.image)
            pygame.PixelArray.replace(textTmp, (0, 21, 130), self.color, 0.15)
            self.image = textTmp.surface
            del textTmp
        except IndexError:
            #print("Index error : Side : {} Key : {:f}/{:d} troup type : {}".format(self.direction,self.animationKey,self.animationKeyMax,self.name))
            pass

        self.image.blit(self.displayText,((self.image.get_width()-self.displayText.get_width())/2,self.image.get_height()-self.displayText.get_height()))
        self.rect = self.image.get_rect(midbottom=self.pygameSim.convertCartToIso((self.x, self.y)))

class PygameView(BattleView):
    def __init__(self, model : BattleModel, controller):
        super().__init__(model, controller)

        self.model = model
        self.controller = controller

        #---MAP & WINDOW CONST---
        self.MAP_HEIGHT = model.map_height
        self.MAP_WIDTH = model.map_width
        self.MAP_DIAG = ((self.MAP_HEIGHT**2 + self.MAP_HEIGHT**2)**0.5)

        self.WINDOW_HEIGHT = PYGAME_WIN[1]
        self.WINDOW_WIDTH = PYGAME_WIN[0]
        self.WINDOW_OFFSET_H = self.WINDOW_HEIGHT / 2
        self.WINDOW_OFFSET_W = self.WINDOW_WIDTH / 2

        self.SCALE = 2
        self.ZOOM = (self.WINDOW_WIDTH+self.WINDOW_HEIGHT)/(self.MAP_WIDTH+self.MAP_HEIGHT)

        #---PYGAME ENV DEFINE---
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("MedievAIl")
        pygame.display.set_icon(pygame.image.load("views/assets/icons/game.png"))
        pygame.mouse.set_cursor(pygame.cursors.Cursor((0,0),pygame.image.load("views/assets/cursors/default32x32.cur")))

        self.font = pygame.font.SysFont('Calibri', 20)
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT),pygame.HWACCEL)

        #---MAP VARIABLES---
        self.MAP_TEXTURE = pygame.image.load('views/assets/grounds/map.png').convert()
        self.map = None
        self.rect = None
        self.mapX = 0
        self.mapY = 0
        #---Unit asset loading--
        self.ASSETS = {}
        for u in LIST_UNITS:
            self.ASSETS[u] = assetLoader(u)

        self.object_list = []
        self.unit_spritegroup = pygame.sprite.Group()

        # --- initialise army 1 units
        for unit in self.model.get_army(self.model.general_1):
            tmp = unit_model(unit,self,pygame.color.Color(0,0,255))
            self.object_list.append(tmp)
            self.unit_spritegroup.add(tmp)

        # --- initialise army 2 units
        for unit in self.model.get_army(self.model.general_2):
            tmp = unit_model(unit,self,pygame.color.Color(255,0,0))
            self.object_list.append(tmp)
            self.unit_spritegroup.add(tmp)

    def makeMap(self,pos_x,pos_y):
        """MAP constructor"""
        self.map = pygame.Surface((self.MAP_WIDTH * 2 * self.SCALE * self.ZOOM, self.MAP_HEIGHT * 2 * self.SCALE * self.ZOOM))
        self.rect = self.map.get_rect(center=(self.WINDOW_OFFSET_W+self.mapX, self.WINDOW_OFFSET_H+self.mapY))
        self.map.fill((0,0,0))
        points = [self.convertCartToIso((pos_x, pos_y)),
              self.convertCartToIso((pos_x+self.MAP_WIDTH, pos_y)),
              self.convertCartToIso((pos_x+self.MAP_WIDTH, pos_y+self.MAP_HEIGHT)),
              self.convertCartToIso((pos_x, pos_y+self.MAP_HEIGHT))]
        pygame.gfxdraw.textured_polygon(self.map, points, self.MAP_TEXTURE, 0, 0)

    def convertCartToIso(self,points):
        """Function to convert cartesian position to isometric position"""
        iso_x = math.floor(((points[0]-points[1])+(self.MAP_WIDTH))*self.SCALE*self.ZOOM)
        iso_y = math.floor((((points[0]+points[1])/2)+(self.MAP_HEIGHT/2))*self.SCALE*self.ZOOM)
        #print("Unit cord x:{} y:{} iso cord x:{} y:{}".format(points[0],points[1],iso_x, iso_y))
        return [iso_x, iso_y]

    def render(self):
        self.getInput()

        #--- Render MAP & UNITS
        self.window.fill((0,0,0))
        self.makeMap(0,0)
        self.unit_spritegroup.update()
        self.unit_spritegroup.draw(self.map)
        self.window.blit(self.map, self.rect)

        #--- Render UI
        textTmp = "{} | {}".format(self.model.general_1.name, self.model.general_2.name)
        self.window.blit(self.font.render(textTmp,
                             False, (255, 255, 255)), ((self.window.get_width()/2)-self.font.size(textTmp)[0]/2, 0))

        self.window.blit(self.font.render("Running : {} | Speed : {:.2f}x".format(self.model.running,self.controller.game_speed),
                                    False, (255,255,255)),(0,0))

        self.window.blit(self.font.render("ZOOM : {:.2f}x".format(self.ZOOM),
                                  False, (255,255,255)),
                                    (self.window.get_width()-self.font.size("ZOOM : 0.00x")[0],0))
        self.window.blit(self.font.render("space : PAUSE | +/- : ZOOM | ↑↓ : SPEED | ←↑↓→ : MOVE | ESC : QUIT | F11 : TOGGLE WINDOW",
                             False, (255, 255, 255)), (0,self.window.get_height()-self.font.get_height()))
        pygame.display.flip()
        pygame.time.wait(1)

    def getInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_KP_PLUS:
                    self.ZOOM +=0.5
                elif event.key == pygame.K_KP_MINUS:
                    if self.ZOOM > 0.5:
                        self.ZOOM -= 0.5
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

        key = pygame.key.get_pressed()
        if key[pygame.K_KP8]:
            self.mapY += 10
        elif key[pygame.K_KP2]:
            self.mapY -= 10
        elif key[pygame.K_KP4]:
            self.mapX += 10
        elif key[pygame.K_KP6]:
            self.mapX -= 10