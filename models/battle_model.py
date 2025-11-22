import heapq
import json
import math

from models.general import generalFactory
from models.unit import unitFactory
from models.unit import *
from models.order import *
from models.general import *
from models.obstacle import Obstacle
import random


class BattleModel:
    def __init__(self)->None:
        self.general_1 = None
        self.general_2 = None
        self.running = False
        self.map_width = None
        self.map_height = None
        self.delta_time = 0.0
        self.list_objects = []


    def load(self, path:str, ai1:str, ai2:str)->None:
        """Charge le scénario de bataille à partir d'un fichier JSON et initialise les généraux et leurs armées."""
        # load json

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # load map

        map_data = data["map"]
        self.map_width = map_data["width"]
        self.map_height = map_data["height"]

        # load generals

        self.general_1 = generalFactory(ai1, self)
        self.general_2 = generalFactory(ai2, self)

        # load army
        army_data = data["armies"]
        for unit_data in army_data["army1"]:
            unit = unitFactory(
                unit_type=unit_data["type"],
                general=self.general_1,
                x=unit_data["x"],
                y=unit_data["y"],
                battle_model=self
            )
            self.list_objects.append(unit)

        for unit_data in army_data["army2"]:
            unit = unitFactory(
                unit_type=unit_data["type"],
                general=self.general_2,
                x=unit_data["x"],
                y=unit_data["y"],
                battle_model=self
            )
            self.list_objects.append(unit)

    def update(self) -> None:
        """Met à jour l'état de la bataille à chaque tick."""
        # Generals decide in random order
        generals = [g for g in (self.general_1, self.general_2) if g is not None]
        random.shuffle(generals)
        for gen in generals:
            gen.decide()

        # Units act in random order
        units = [obj for obj in self.list_objects if isinstance(obj, Unit)]
        random.shuffle(units)
        for unit in units:
            unit.action.action()


    def pause(self)->None:
        """Met en pause ou reprend la simulation de la bataille."""
        self.running = not self.running

    def save(self, scenario_file:str)->None:
        pass

    
    def is_in_map(self, x, y):
        """Vérification si les coordonnées sont dans les limites de la carte"""
        if self.map_width is None or self.map_height is None:
            return False
        return 0 <= x < self.map_width and 0 <= y < self.map_height
    
    def is_obstacle_at(self, x, y):
        """Vérification de si un obstacle se trouve à la position (x, y)"""
        for obj in self.list_objects:
            if isinstance(obj, Obstacle) and obj.x == x and obj.y == y:
                return True
        return False

    
    def shortest_path(self, start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Mini pathfinding :
        - déplace vers les coordonnés en ligne droite
        - si bloqué : esquive à gauche puis à droite
        - sinon avance en X ou Y seul
        - renvoie un tuple avec le prochain pas ou None
        """

        x, y = start
        tx, ty = end

        # Déjà à destination
        if (x, y) == (tx, ty):
            return None   # rien à faire

        # Direction vers la cible
        dx = 0
        dy = 0

        if tx > x: dx = 1
        elif tx < x: dx = -1

        if ty > y: dy = 1
        elif ty < y: dy = -1

        # ESSAI 1 : ligne droite
        nx, ny = x + dx, y + dy
        if self.is_in_map(nx, ny) and not self.is_obstacle_at(nx, ny):
            return (nx, ny)

        # ESSAI 2 : esquive à gauche
        lx, ly = x - dy, y + dx
        if self.is_in_map(lx, ly) and not self.is_obstacle_at(lx, ly):
            return (lx, ly)

        # ESSAI 3 : esquive à droite
        rx, ry = x + dy, y - dx
        if self.is_in_map(rx, ry) and not self.is_obstacle_at(rx, ry):
            return (rx, ry)

        # ESSAI 4 : avancer seulement en X si possible
        if dx != 0:
            nx2 = x + dx
            if self.is_in_map(nx2, y) and not self.is_obstacle_at(nx2, y):
                return (nx2, y)

        # ESSAI 5 : avancer seulement en Y si possible
        if dy != 0:
            ny2 = y + dy
            if self.is_in_map(x, ny2) and not self.is_obstacle_at(x, ny2):
                return (x, ny2)

        # Aucun mouvement possible
        return None

    
    def get_army(self, general: General) -> list[Unit]:
        """Retourne la liste des unités appartenant au général spécifié."""
        return [
            obj for obj in self.list_objects
            if isinstance(obj, Unit) and obj.general == general and obj.is_alive()
        ]
    
    def get_enemy_army(self, general: General) -> list[Unit]:
        """Retourne la liste des unités ennemies par rapport au général spécifié."""
        return [
            obj for obj in self.list_objects
            if isinstance(obj, Unit) and obj.general != general and obj.is_alive()
        ]
