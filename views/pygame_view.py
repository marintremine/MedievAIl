from views.battle_view import BattleView
from models.battle_model import BattleModel
from settings import PYGAME_WIN
import pygame
import pygame.gfxdraw
import math
import json

MINIMAP_SIZE = (300, 300)
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


class miniMap(pygame.sprite.Sprite):
    def __init__(self,pygamesSim):
        super().__init__()
        self.visible = False
        self.pygamesSim = pygamesSim
        self.image = pygame.Surface(MINIMAP_SIZE)
        self.rect = self.image.get_rect(topright=(PYGAME_WIN[0],0))
        self.width = 2
        self.scale_x = MINIMAP_SIZE[0] / self.pygamesSim.window.get_size()[0]
        self.scale_y = MINIMAP_SIZE[1] / self.pygamesSim.window.get_size()[1]

        self.scaleMap_x = MINIMAP_SIZE[0]/(self.pygamesSim.MAP_WIDTH*self.pygamesSim.SCALE)
        self.scaleMap_y = MINIMAP_SIZE[0]/(self.pygamesSim.MAP_WIDTH*self.pygamesSim.SCALE)

    def update(self):
        """Update the minimap"""
        self.image.fill((69, 69, 69))
        self.rect = self.image.get_rect(topright=(self.pygamesSim.window.get_width()-1,0))
        self.makeMap(-self.pygamesSim.mapX,-self.pygamesSim.mapY)

    def makeMap(self,pos_x,pos_y):
        """MAP constructor"""

        self.scale_x = MINIMAP_SIZE[0]/self.pygamesSim.window.get_size()[0]
        self.scale_y = MINIMAP_SIZE[1]/self.pygamesSim.window.get_size()[1]

        self.scaleMap_x = MINIMAP_SIZE[0]/(self.pygamesSim.MAP_WIDTH*2)
        self.scaleMap_y = MINIMAP_SIZE[1]/(self.pygamesSim.MAP_HEIGHT*2)

        windowX = self.pygamesSim.window.get_width()
        windowY = self.pygamesSim.window.get_height()

        #Create the map surface on the minimap

        tmpSurf = pygame.Surface((self.pygamesSim.MAP_WIDTH * 2 * self.scaleMap_x, self.pygamesSim.MAP_HEIGHT  * self.scaleMap_y)).convert_alpha()
        tmpSurf.fill((0,0,0,0))

        points = [self.convertPos((0, 0)),
                  self.convertPos((self.pygamesSim.MAP_WIDTH, 0)),
                  self.convertPos((self.pygamesSim.MAP_WIDTH, self.pygamesSim.MAP_HEIGHT)),
                  self.convertPos((0, self.pygamesSim.MAP_HEIGHT))]

        pygame.draw.polygon(tmpSurf,(0,255,0), points)
        tmprect = tmpSurf.get_rect(center = (MINIMAP_SIZE[0]/2, MINIMAP_SIZE[1]/2))

        #Populate minimap with units

        for u in self.pygamesSim.object_list:
            if u.is_alive:
                pygame.draw.circle(tmpSurf,u.color,self.convertPos((u.x,u.y)),3)

        #Create the windows frame on the minimap

        self.image.blit(tmpSurf, tmprect)

        tmpSurf = pygame.Surface((((windowX * self.scale_x)  / (self.pygamesSim.ZOOM * self.pygamesSim.SCALE)) + self.width,
                                  ((windowY * self.scale_y)  / (self.pygamesSim.ZOOM * self.pygamesSim.SCALE)) + self.width)).convert_alpha()
        tmpSurf.fill((0,0,0,0))

        points = [(0, 0),
                  (((windowX * self.scale_x)  / (self.pygamesSim.ZOOM * self.pygamesSim.SCALE)),0),
                  (((windowX * self.scale_x)  / (self.pygamesSim.ZOOM * self.pygamesSim.SCALE)), ((windowY * self.scale_y)  / (self.pygamesSim.ZOOM * self.pygamesSim.SCALE))),
                  (0, ((windowY * self.scale_y)  / (self.pygamesSim.ZOOM * self.pygamesSim.SCALE)))]

        pygame.draw.polygon(tmpSurf,(255,255,255), points,width=self.width)
        rect = tmpSurf.get_rect(center=((pos_x * self.scale_x) + MINIMAP_SIZE[0] / 2, (pos_y * self.scale_y) + MINIMAP_SIZE[1] / 2))



        self.image.blit(tmpSurf,rect)

    def mapTouch(self,pos):
        """Calculate the position of the touch on the minimap"""
        windowX = self.pygamesSim.window.get_width()
        coordX = pos[0] - (windowX - MINIMAP_SIZE[0])
        coordY = pos[1]

        if ((windowX - MINIMAP_SIZE[0]) <= pos[0] <= windowX and
                pos[1] <= MINIMAP_SIZE[1]):

            return [coordX/self.scale_x, coordY/self.scale_y]
        else:
            return None

    def convertPos(self,pos):
        """Convert cartesian coordinates to isometric coordinates"""
        iso_X = ((pos[0]-pos[1])+self.pygamesSim.MAP_WIDTH)*self.scaleMap_x
        iso_Y = ((pos[0] + pos[1]) / 2) * self.scaleMap_y
        return [iso_X, iso_Y]

    def toggleVisible(self):
        """Toggle visible minimap"""
        self.visible = not self.visible


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
                    self.action = "dead"
            else:
                if self.animationKey > self.animationKeyMax:
                    self.animationKey = 0
                else:
                    self.animationKey += 0.1

        #Create the textured polygon for the map
        if self.action != "dead":
            try:
                self.image = self.TEXTURE[self.animation][switchOrientation[str(self.direction)]][math.floor(self.animationKey)]
                self.image = pygame.transform.scale(
                    self.image,
                    ((self.image.get_width()/self.pygameSim.SCALE),
                     (self.image.get_height()/self.pygameSim.SCALE))
                )
                textTmp = pygame.PixelArray(self.image)
                pygame.PixelArray.replace(textTmp, (0, 21, 130), self.color, 0.15)
                self.image = textTmp.surface
                del textTmp
            except IndexError:
                pass
            if self.is_alive:
                pass #self.image.blit(self.displayText,((self.image.get_width()-self.displayText.get_width())/2,self.image.get_height()-self.displayText.get_height()))

        else:
            self.image.set_alpha(0)
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
        self.ZOOM = 1

        #---PYGAME ENV DEFINE---
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("MedievAIl")
        pygame.display.set_icon(pygame.image.load("views/assets/icons/game.png"))
        pygame.mouse.set_cursor(pygame.cursors.Cursor((0,0),pygame.image.load("views/assets/cursors/default32x32.cur")))

        self.font = pygame.font.SysFont('Calibri', 20)
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT),pygame.HWSURFACE | pygame.DOUBLEBUF)

        #---MAP VARIABLES---
        self.MAP_TEXTURE = pygame.image.load('views/assets/grounds/map.png').convert()
        self.map = None
        self.rect = None
        self.mapX = 0
        self.mapY = 0

        #---GUI---

        self.commandText = self.font.render(" P : PAUSE/PLAY | +/-/MOUSE WHEEL : ZOOM | +/- : SPEED | ZQSD : MOVE | M : MINIMAP | ESC : QUIT | F10 : FULLSCREEN | F11 : SAVE",False, (255, 255, 255))
        self.generalNameText = self.font.render("{} | {}".format(self.model.general_1.name, self.model.general_2.name),False, (255, 255, 255))

        self.miniMap = miniMap(self)
        self.miniMapGrp = pygame.sprite.Group()
        self.miniMapGrp.add(self.miniMap)
        #---Unit asset loading--
        self.ASSETS = {}
        for u in LIST_UNITS:
            self.ASSETS[u] = assetLoader(u)

        self.object_list = []
        self.unit_spritegroup = pygame.sprite.Group()

        # --- initialise army 1 units
        for unit in self.model.get_army(self.model.general_1):
            tmp = unit_model(unit,self,pygame.color.Color(255,0,0))
            self.object_list.append(tmp)

        # --- initialise army 2 units
        for unit in self.model.get_army(self.model.general_2):
            tmp = unit_model(unit,self,pygame.color.Color(0,0,255))
            self.object_list.append(tmp)

    def makeMap(self,pos_x,pos_y):
        """MAP constructor"""
        self.map = pygame.Surface((self.MAP_WIDTH * 2 * self.SCALE, self.MAP_HEIGHT * 2 * self.SCALE))
        self.map.fill((0,0,0))
        points = [self.convertCartToIso((pos_x, pos_y)),
              self.convertCartToIso((pos_x+self.MAP_WIDTH, pos_y)),
              self.convertCartToIso((pos_x+self.MAP_WIDTH, pos_y+self.MAP_HEIGHT)),
              self.convertCartToIso((pos_x, pos_y+self.MAP_HEIGHT))]
        pygame.gfxdraw.textured_polygon(self.map, points, self.MAP_TEXTURE, 0, 0)

    def convertCartToIso(self,points):
        """Function to convert cartesian position to isometric position"""
        iso_x = math.floor(((points[0]-points[1])+(self.MAP_WIDTH))*self.SCALE)
        iso_y = math.floor((((points[0]+points[1])/2)+(self.MAP_HEIGHT/2))*self.SCALE)
        return [iso_x, iso_y]

    def sortingUnits(self,word):
        return word.x*word.y

    def updateSpriteGroup(self):
        """Method to update and order sprite group
        used to resolve z-axis error"""
        self.object_list.sort(key=self.sortingUnits)
        for unit in self.object_list:
            self.unit_spritegroup.add(unit)

    def render(self):
        """Function to render the game screen"""
        self.getInput()
        #--- Render MAP & UNITS
        self.window.fill((0,0,0))
        self.makeMap(0,0)
        self.updateSpriteGroup()
        self.unit_spritegroup.update()
        self.unit_spritegroup.draw(self.map)
        self.map = pygame.transform.smoothscale_by(self.map,self.ZOOM)
        self.rect = self.map.get_rect(center=(self.window.get_width()/2 + self.mapX, self.window.get_height()/2 + self.mapY))
        self.window.blit(self.map, self.rect)

        if self.miniMap.visible:
            self.miniMapGrp.update()
            self.miniMapGrp.draw(self.window)

        #--- Render UI

        self.window.blit(self.generalNameText, ((self.window.get_width()/2)-self.generalNameText.get_width()/2, 0))

        self.window.blit(self.font.render("Running : {} | Speed : {:.2f}x".format(self.model.running,self.controller.game_speed),
                                    False, (255,255,255)),(0,0))

        self.window.blit(self.font.render("ZOOM : {:.2f}x".format(self.ZOOM),
                                  False, (255,255,255)),
                                    (self.window.get_width()-self.font.size("ZOOM : 0.00x")[0],0))
        self.window.blit(self.commandText, (0,self.window.get_height()-self.font.get_height()))

        pygame.display.flip()
        self.unit_spritegroup.empty()
        pygame.time.wait(1)

    def getInput(self):
        """Method who get all input for the pygame view"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_PLUS:
                    self.zoomIn()
                elif event.key == pygame.K_KP_MINUS:
                    self.zoomOut()
                elif event.key == pygame.K_F10:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_m:
                    self.miniMap.toggleVisible()

            elif event.type == pygame.MOUSEWHEEL:
                if event.y == 1:
                    self.zoomIn()
                elif event.y == -1:
                    self.zoomOut()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.moveMinimap(event.pos)

        #Its more faster to use pygames build-in keyboard event than use an external API
        key = pygame.key.get_pressed()
        if key[pygame.K_z]:
            self.mapY += 10*self.ZOOM
        elif key[pygame.K_s]:
            self.mapY -= 10*self.ZOOM
        elif key[pygame.K_q]:
            self.mapX += 10*self.ZOOM
        elif key[pygame.K_d]:
            self.mapX -= 10*self.ZOOM

    def zoomIn(self):
        self.ZOOM += 0.5

    def zoomOut(self):
        if self.ZOOM > 0.5:
            self.ZOOM -= 0.5

    def moveMinimap(self,pos):
        if self.miniMap.visible:
            tmpPos = self.miniMap.mapTouch(pos)
            if tmpPos != None:
                self.mapX = (self.window.get_width() / 2) - tmpPos[0]
                self.mapY = (self.window.get_height() / 2) - tmpPos[1]