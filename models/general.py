from __future__ import annotations
import random

from models.order import Attack, Move, Wait, Defense
from models.unit import *

class General:
    def __init__(self, name: str, battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        self.name = name
        self.battle_model = battle_model

    def get_closest_enemy(self, unit, enemy_list):
        """
        Trouve l'ennemi le plus proche dans une liste donnée en utilisant la distance de Manhattan
        """
        alive_enemies = (enemy for enemy in enemy_list if enemy.is_alive())
        manhattan = lambda enemy: abs(unit.x - enemy.x) + abs(unit.y - enemy.y)
        return min(
            alive_enemies,
            key=manhattan,
            default=None
        )

    def manhattan(self, a, b):
        """
        Renvoie la manhattan
        """
        return abs(a.x - b.x) + abs(a.y - b.y)

    def decide(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.name}"

class Daft(General):
    def __init__(self, battle_model):
        super().__init__("Daft", battle_model)
    def decide(self) -> None:
        pass

class BrainDead(General):
    """
    Un général qui ne donne aucun ordre, toute l'armée est en mode Defense donc les unités attaquent les ennemis dans leur portée.
    """
    def __init__(self, battle_model):
        super().__init__("BrainDead", battle_model)

    def decide(self) -> None:
        for unit in self.battle_model.get_army(self):
            unit.action = Defense(unit)


class Aegis(General):
    """
    Un général qui privilégie la contre-attaque : ses Knight tiennent la position
    sous la couverture des Crossbowman et ne chargent que lorsque l'affrontement est favorable.
    """

    def __init__(self, battle_model):
        super().__init__("Aegis", battle_model)

    def has_crossbow_support(self, unit):
        """
        Vérifie si l'unité a un support archer
        """
        for ally in self.battle_model.get_army(self):
            if not ally.is_alive():
                continue
            if ally is unit:
                continue
            if ally.name == "Crossbowman" and self.manhattan(unit, ally) <= 5:
                return True
        return False

    def get_best_enemy(self, unit, enemies):
        """
        Choisie le meilleur enemies à cibler en attribuant un score en fonction du type
        """
        best_enemy = None
        best_score = None
        for enemy in enemies:
            score = -(self.manhattan(unit, enemy))
            if unit.name == "Knight" and enemy.name == "Crossbowman":
                score += 3
            if unit.name == "Knight" and enemy.name == "Pikeman" and self.manhattan(unit, enemy) > 2:
                score -= 5
            if best_score is None or score > best_score:
                best_score = score
                best_enemy = enemy
                print(best_score)
        return best_enemy

    def decide(self) -> None:
        enemies = self.battle_model.get_enemy_army(self)
        if not enemies:
            return

        for unit in self.battle_model.get_army(self):
            if not isinstance(unit.action, Wait):
                continue

            target = self.get_best_enemy(unit, enemies)
            if not target:
                unit.action = Wait(unit)
                continue

            if unit.name != "Knight":
                unit.action = Attack(unit, target)
                continue

            if self.manhattan(unit, target) <= 2:
                unit.action = Attack(unit, target)
            elif target.name == "Pikeman" and self.has_crossbow_support(unit):
                unit.action = Wait(unit)
            else:
                unit.action = Attack(unit, target)

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
        self.posx_last_pike = 0
        self.posy_last_pike = 0
        
    def is_anyone_there(self, px, py, ux, uy, R):
        dx = ux - px
        dy = uy - py
        distance = (dx*dx + dy*dy)**0.5
        return distance <= R
    
    def dist_ht_2(self, x1, y1, x2, y2):
        distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return distance >= 2


    def decide(self):
        enemy_units = self.battle_model.get_enemy_army(self)
        if not enemy_units:
            return
        n = len(enemy_units)
        avg_x = sum(u.x for u in enemy_units) / n
        avg_y = sum(u.y for u in enemy_units) / n
        for unit in self.battle_model.get_army(self):
            dx = avg_x - unit.x
            dy = avg_y- unit.y
            distance = (dx*dx + dy*dy) ** 0.5
            if distance == 0:
                distance = 1
            new_x = unit.x+dx / distance
            new_y = unit.y+dy / distance
            nearest = min(enemy_units, key=lambda e: (e.x - unit.x)**2 + (e.y - unit.y)**2)
            dist2 = (nearest.x - unit.x)**2 + (nearest.y - unit.y)**2

            #Pikeman
            if isinstance(unit, Pikeman):
                self.posx_last_pike = unit.x
                self.posy_last_pike = unit.y
                if abs(avg_x-unit.x) <=3 and abs(avg_y -unit.y) <= 3:
                    unit.action = Attack(unit, nearest)
                    # if dist2 <= 4: 
                    #     unit.action = Attack(unit, nearest)
                else :
                    for u in enemy_units :
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x , u.y, 2)
                    if not anyone :
                        unit.action = Attack(unit, nearest)
                    else :
                        unit.action = Move(unit, new_x, new_y)

            # Knights
            if isinstance(unit, Knight):
                if self.posx_last_pike != 0 and self.posy_last_pike != 0:
                    if self.dist_ht_2(unit.x, unit.y, self.posx_last_pike, self.posy_last_pike):
                        Wait(unit)
                        
                if abs(avg_x-unit.x) <= 3 and abs(avg_y-unit.y) <= 3:
                    unit.action = Attack(unit, nearest)
                else:
                    for u in enemy_units:
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x, u.y, 2)
                    if not anyone:
                        unit.action = Attack(unit, nearest)
                    else:
                        unit.action = Move(unit, new_x, new_y)

            #Crossbowman
            if isinstance(unit, Crossbowman):
                if abs(avg_x-unit.x) <=3 and abs(avg_y -unit.y) <= 3:
                    unit.action = Attack(unit, nearest)
                    # if dist2 <= 4: 
                    #     unit.action = Attack(unit, nearest)
                else :
                    for u in enemy_units :
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x , u.y, 2)
                    if not anyone :
                        unit.action = Attack(unit, nearest)
                    else :
                        unit.action = Move(unit, new_x, new_y)
            anyone = False

def generalFactory(general_type: str, battle_model) -> General:
    general_classes = {
        "daft": Daft,
        "braindead": BrainDead,
        "aegis": Aegis,
        "movetest": MoveTestGeneral,
        "attacktest": AttackTestGeneral,
        "momoia": MomoIA
    }
    key = general_type.lower()
    if key in general_classes:
        return general_classes[key](battle_model)
    else:
        raise ValueError(f"Unknown general type: {key}")


