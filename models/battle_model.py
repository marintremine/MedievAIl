import json
import os
from pathlib import Path
import random
from jinja2 import Environment, FileSystemLoader

from models.general import *
from models.unit import *
from models.order import *
from models.general import *
from models.obstacle import *

class BattleModel:
    def __init__(self)->None:
        self.general_1 = None
        self.general_2 = None
        self.running = False
        self.map_width = None
        self.map_height = None
        self.delta_time = 0.0
        self.list_objects = []
        self.winner = None


    def reset(self)->None:
        """Réinitialise le modèle de bataille."""
        self.general_1 = None
        self.general_2 = None
        self.map_width = None
        self.map_height = None
        self.list_objects = []
        self.winner = None

    def load(self, path:str, general_1:General, general_2:General)->None:
        """Charge le scénario de bataille à partir d'un fichier JSON et initialise les généraux et leurs armées."""

        # assign generals
        self.general_1 = general_1
        self.general_2 = general_2

        # load json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # load map
        self.map_width = data["map_width"]
        self.map_height = data["map_height"]

        # load army
        for unit_data in data["army1"]:
            unit = unitFactory(
                unit_type=unit_data["type"],
                general=self.general_1,
                x=unit_data["x"],
                y=unit_data["y"],
                battle_model=self
            )
            if "hp" in unit_data:
                unit.hp = unit_data["hp"]
            if "cooldown_timer" in unit_data:
                unit.cooldown_timer = unit_data["cooldown_timer"]
            if "move_progress" in unit_data:
                unit.move_progress = unit_data["move_progress"]

            self.list_objects.append(unit)
            # Load obstacles (if any)
            for obs_data in data.get("obstacles", []):
            # Create the unit obstacle and then make the ifs
                obstacle = ObstacleFactory(
                    obs_type=obs_data.get("type", "obstacle"),
                    x=obs_data["x"],
                    y=obs_data["y"],
                    battle_model=self,
                    )
                self.list_objects.append(obstacle)


        for unit_data in data["army2"]:
            unit = unitFactory(
                unit_type=unit_data["type"],
                general=self.general_2,
                x=unit_data["x"],
                y=unit_data["y"],
                battle_model=self
            )
            if "hp" in unit_data:
                unit.hp = unit_data["hp"]
            if "cooldown_timer" in unit_data:
                unit.cooldown_timer = unit_data["cooldown_timer"]
            if "move_progress" in unit_data:
                unit.move_progress = unit_data["move_progress"]

            self.list_objects.append(unit)


    def save(self, scenario_file: str = None) -> None:
        """
        Enregistre l'état actuel de la bataille dans un fichier JSON.
        """
        data = self.to_dict()
        scenarios_dir = Path("scenarios")
        scenarios_dir.mkdir(parents=True, exist_ok=True)

        if not scenario_file:
            base, ext = "saved_scenario", ".json"
        else:
            base, ext = os.path.splitext(scenario_file)
            if ext == "":
                ext = ".json"

        candidate = f"{base}{ext}"
        counter = 0
        while (scenarios_dir / candidate).exists():
            counter += 1
            candidate = f"{base}_{counter}{ext}"

        with open(scenarios_dir / candidate, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def snapshot_html(self) -> None:
        """
        Génère un snapshot HTML du modèle de bataille
        """
        file_loader = FileSystemLoader('templates') 
        env = Environment(loader=file_loader)
        template = env.get_template('snapshot.html')
        html = template.render(model=self)
        
        snapshots_dir = Path("snapshots")
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        with open(snapshots_dir / 'snapshot.html', "w", encoding="utf-8") as f:
            f.write(html)



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

        # Check for end of battle
        army1_alive = any(isinstance(obj, Unit) and obj.general == self.general_1 and obj.is_alive() for obj in self.list_objects)
        army2_alive = any(isinstance(obj, Unit) and obj.general == self.general_2 and obj.is_alive() for obj in self.list_objects)
        if army1_alive and not army2_alive:
            self.winner = self.general_1
        if army2_alive and not army1_alive:
            self.winner = self.general_2

    def pause(self)->None:
        """Met en pause ou reprend la simulation de la bataille."""
        self.running = not self.running

    
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
    
    def to_dict(self):
        return {
            "map_width": self.map_width,
            "map_height": self.map_height,
            "army1": [
                obj.to_dict() for obj in self.list_objects if isinstance(obj, Unit) and obj.general == self.general_1
            ],
            "army2": [
                obj.to_dict() for obj in self.list_objects if isinstance(obj, Unit) and obj.general == self.general_2
            ],
            "obstacles": [
                obj.to_dict() for obj in self.list_objects if isinstance(obj, Obstacle)
            ],
        }
