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
        self.objects = {
            'obstacles': set(),
            'units': set(),
            'armies': {},
            'state_map': {}
        }
        self.winner = None
    

    def reset(self)->None:
        """Réinitialise le modèle de bataille."""
        self.general_1 = None
        self.general_2 = None
        self.map_width = None
        self.map_height = None
        self.objects = {
            'obstacles': set(),
            'units': set(),
            'armies': {},
            'state_map': {}
        }
        self.winner = None

    def load(self, data, general_1:General, general_2:General)->None:
        """Charge le scénario de bataille à partir d'un fichier JSON et initialise les généraux et leurs armées."""

        self.reset()

        # assign generals
        self.general_1 = general_1
        self.general_2 = general_2

        if isinstance(data, str):
            with open(data, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
        else:
            loaded_data = data

        self.objects['armies'][self.general_1] = set()
        self.objects['armies'][self.general_2] = set()

        
            
        # load map
        self.map_width = loaded_data["map_width"]
        self.map_height = loaded_data["map_height"]

        self.objects['state_map'] = {}
        for x in range(self.map_width):
            for y in range(self.map_height):
                self.objects['state_map'][(x, y)] = set()

        armies_data = [
            (loaded_data.get("army1", []), self.general_1),
            (loaded_data.get("army2", []), self.general_2)
        ]

        # load army
        for army_list, general in armies_data:
            for unit_data in army_list:
                # Création
                unit = unitFactory(
                    unit_type=unit_data["type"],
                    general=general,
                    x=unit_data["x"],
                    y=unit_data["y"],
                    battle_model=self
                )
                
                # Restauration des stats
                unit.hp = unit_data.get("hp", unit.hp)
                
                # Timers
                unit.current_reload_time = unit_data.get("current_reload_time", 0)
                unit.current_attack_delay = unit_data.get("current_attack_delay", 0)
                unit.move_progress = unit_data.get("move_progress", 0)

                # Etat actuel
                unit.currentAction = "stand" 

                # Enregistrement dans les collections
                self.objects['units'].add(unit)
                self.objects['armies'][general].add(unit)
                self.objects['state_map'][(unit.x, unit.y)].add(unit)


        # load obstacles
        for obs_data in loaded_data.get("obstacles", []):
            obstacle = ObstacleFactory(
                obs_type=obs_data.get("type", "obstacle"),
                x=obs_data["x"],
                y=obs_data["y"],
                battle_model=self,
                )
            self.objects['obstacles'].add(obstacle)
            self.objects['state_map'][(obstacle.x, obstacle.y)].add(obstacle)

        print(f"BattleModel loaded from with {len(self.objects['units'])} units and {len(self.objects['obstacles'])} obstacles.")


    # def save(self, scenario_file: str = None) -> None:
    #     """
    #     Enregistre l'état actuel de la bataille dans jun fichier JSON.
    #     """
    #     data = self.to_dict()
    #     scenarios_dir = Path("scenarios")
    #     scenarios_dir.mkdir(parents=True, exist_ok=True)

    #     if not scenario_file:
    #         base, ext = "saved_scenario", ".json"
    #     else:
    #         base, ext = os.path.splitext(scenario_file)
    #         if ext == "":
    #             ext = ".json"

    #     candidate = f"{base}{ext}"
    #     counter = 0
    #     while (scenarios_dir / candidate).exists():
    #         counter += 1
    #         candidate = f"{base}_{counter}{ext}"

    #     with open(scenarios_dir / candidate, "w", encoding="utf-8") as f:
    #         json.dump(data, f, indent=4)

    def save(self) -> dict:
        """
        Enregistre l'état actuel de la bataille dans un dictionnaire.
        """
        data = self.to_dict()
        print(f"BattleModel saved with {len(self.objects['units'])} units and {len(self.objects['obstacles'])} obstacles.")
        return data

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

    def remove_unit(self, unit: Unit) -> None:
        """Supprime une unité du modèle de bataille."""
        self.objects['units'].discard(unit)
        
        if unit.general in self.objects['armies']:
            self.objects['armies'][unit.general].discard(unit)
            
        coord = (unit.x, unit.y)
        if coord in self.objects['state_map']:
            self.objects['state_map'][coord].discard(unit)


    def update(self) -> None:
        """Met à jour l'état de la bataille à chaque tick."""

        # Generals decide in random order
        generals = [g for g in (self.general_1, self.general_2) if g is not None]
        random.shuffle(generals)
        for gen in generals:
            gen.decide()

        for unit in list(self.objects['units']):
            unit.action()

        dead_units = [u for u in self.objects['units'] if not u.is_alive()]
        for dead in dead_units:
            self.remove_unit(dead)
                
        # Check for end of battle
        army1_alive = len(self.objects['armies'][self.general_1]) > 0
        army2_alive = len(self.objects['armies'][self.general_2]) > 0
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
        for obj in self.objects['state_map'].get((x, y), set()):
            if isinstance(obj, Obstacle):
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

    def get_units(self) -> set[Unit]:
        """Retourne l'ensemble des unités dans le modèle de bataille."""
        return self.objects['units']
    
    def get_obstacles(self) -> set[Obstacle]:
        """Retourne l'ensemble des obstacles dans le modèle de bataille."""
        return self.objects['obstacles']
    
    def get_army(self, general: General) -> set[Unit]:
        """Retourne l'ensemble des unités appartenant au général spécifié."""
        return self.objects['armies'].get(general, set())
    
    def get_enemy_army(self, general: General) -> set[Unit]:
        """Retourne l'ensemble des unités ennemies par rapport au général spécifié."""
        enemies = set()
        for gen, army in self.objects['armies'].items():
            if gen != general:
                enemies.update(army)
        return enemies
    
    def to_dict(self):
        return {
            "map_width": self.map_width,
            "map_height": self.map_height,
            "army1": [
                unit.to_dict() for unit in self.objects['armies'][self.general_1]
            ],
            "army2": [
                unit.to_dict() for unit in self.objects['armies'][self.general_2]
            ],
            "obstacles": [
                obstacle.to_dict() for obstacle in self.objects['obstacles']
            ],
        }
