import json

from models.general import generalFactory
from models.unit import unitFactory
from models.unit import *
from models.order import *
from models.general import *
from models.obstacle import *
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
        return 0 <= x < self.map_width and 0 <= y < self.map_height
    
    def is_obstacle_at(self, x, y):
        """Vérification de si un obstacle se trouve à la position (x, y)"""
        for obj in self.list_objects:
            if isinstance(obj, Obstacle) and obj.x == x and obj.y == y:
                return True
        return False

    def shortest_path(self, start:tuple[int, int], end:tuple[int, int])->list[tuple[int, int]]:

        """
        Recherche le plus court chemin entre deux coordonnées sur une grille en utilisant l'algorithme BFS.
        Il effectue plusieurs vérifications
        - Si la nouvelle position est dans les limites de la carte
        - Si elle n'a pas déjà été visitée
        - S'il n'y a pas d'obstacle à cette position.

        Parameters
        ----------
        start_x : int
            Coordonnée X de départ.
        start_y : int
            Coordonnée Y de départ.
        goal_x : int
            Coordonnée X d'arrivée.
        goal_y : int
            Coordonnée Y d'arrivée.

        Returns
        -------
        list[tuple[int, int]]
            Liste ordonnée des coordonnées constituant le chemin trouvé.
            Retourne une liste vide si aucun chemin n'existe.
        """

        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        start_x, start_y = start
        end_x, end_y = end

        visited = set()
        queue = [(start_x, start_y, [(start_x, start_y)])]
        visited.add((start_x, start_y))

        while queue:
            x, y, path = queue.pop(0)
            if (x, y) == (end_x, end_y):
                return path

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (self.is_in_map(nx, ny) and (nx, ny) not in visited and not self.is_obstacle_at(nx, ny)):
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + [(nx, ny)]))
        return []
    
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