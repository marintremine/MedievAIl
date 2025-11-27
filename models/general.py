from __future__ import annotations
import random

from models.order import Attack, Move, Wait
from models.unit import *

class General:
    def __init__(self, name: str, battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        self.name = name
        self.battle_model = battle_model

    def decide(self) -> None:
        pass

class Daft(General):
    def __init__(self, battle_model):
        super().__init__("Daft", battle_model)
    def decide(self) -> None:
        pass

class BrainDead(General):
    def __init__(self, battle_model):
        super().__init__("BrainDead", battle_model)

    def decide(self) -> None:
        pass

class MoveTestGeneral(General):
    """
    Un général qui ordonne à chaque unité de se déplacer vers des coordonnées aléatoires sur la carte si elle est en attente.
    """
    def __init__(self, battle_model):
        super().__init__("MoveTestGeneral", battle_model)

    def decide(self) -> None:
        for unit in self.battle_model.get_army(self):
            if isinstance(unit, Unit) and unit.is_alive() and isinstance(unit.action, Wait):
                # pick random coords inside the map 
                new_x = random.randrange(0, self.battle_model.map_width)
                new_y = random.randrange(0, self.battle_model.map_height)

                unit.action = Move(unit, new_x, new_y)

class AttackTestGeneral(General):
    """
    Un général qui ordonne à chaque unité d'attaquer une unité ennemie aléatoire si elle est en attente.
    """
    def __init__(self, battle_model):
        super().__init__("AttackTestGeneral", battle_model)

    def decide(self) -> None:
        enemy_units = self.battle_model.get_enemy_army(self)
        for unit in self.battle_model.get_army(self):
            if unit.is_alive() and isinstance(unit.action, Wait):
                if enemy_units:
                    # choose a random enemy unit to attack
                    target = random.choice(enemy_units)
                    unit.action = Attack(unit, target)
                else:
                    unit.action = Wait(unit)

class MomoIA(General):
    def __init__(self, battle_model):
        super().__init__("MomoIA", battle_model)

    def decide(self):
        enemy_units = self.battle_model.get_enemy_army(self)
        n = len(enemy_units)
        avg_x = sum(u.x for u in enemy_units) / n
        avg_y = sum(u.y for u in enemy_units) / n
        for unit in self.battle_model.get_army(self):
                # Knights
                if isinstance(unit, Knight) and isinstance(unit.action, Wait):
                    nearest = min(enemy_units, key=lambda e: (e.x - unit.x)**2 + (e.y - unit.y)**2)
                    dist2 = (nearest.x - unit.x)**2 + (nearest.y - unit.y)**2

                    # Attaque si proche
                    if dist2 <= 4: 
                        unit.action = Attack(unit, nearest)
                    else :
                        dx = avg_x - unit.x
                        dy = avg_y- unit.y
                        distance = (dx*dx + dy*dy) ** 0.5
                        unit.action = Move(unit, unit.x+dx / distance, unit.y+dy / distance)
                else :
                    unit.action = Wait(unit)

                #Crossbowman
                if isinstance(unit, Crossbowman):
                    nearest = min(enemy_units, key=lambda e: (e.x - unit.x)**2 + (e.y - unit.y)**2)
                    dist2 = (nearest.x - unit.x)**2 + (nearest.y - unit.y)**2
                    # Attaque si proche
                    if dist2 <= 4: 
                        unit.action = Attack(unit, nearest)
                    else :
                        dx = avg_x - unit.x
                        dy = avg_y- unit.y
                        distance = (dx*dx + dy*dy) ** 0.5
                        unit.action = Move(unit, unit.x+dx / distance, unit.y+dy / distance)
                else :
                    unit.action = Wait(unit)
                
                #Pikeman
                if isinstance(unit, Pikeman) and isinstance(unit.action, Wait):
                    nearest = min(enemy_units, key=lambda e: (e.x - unit.x)**2 + (e.y - unit.y)**2)
                    dist2 = (nearest.x - unit.x)**2 + (nearest.y - unit.y)**2
                    # Attaque si proche
                    if dist2 <= 4: 
                        unit.action = Attack(unit, nearest)
                    else :
                        dx = avg_x - unit.x
                        dy = avg_y- unit.y
                        distance = (dx*dx + dy*dy) ** 0.5
                        unit.action = Move(unit, unit.x+dx / distance, unit.y+dy / distance)
                else :
                    unit.action = Wait(unit)


def generalFactory(general_type: str, battle_model) -> General:
    general_classes = {
        "daft": Daft,
        "braindead": BrainDead,
        "movetest": MoveTestGeneral,
        "attacktest": AttackTestGeneral,
        "momoia": MomoIA
    }
    key = general_type.lower()
    if key in general_classes:
        return general_classes[key](battle_model)
    else:
        raise ValueError(f"Unknown general type: {key}")