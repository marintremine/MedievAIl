from __future__ import annotations
import random

from models.order import Attack, Move, Wait, Defense
from models.unit import *

class General:
    def __init__(self, name: str, battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        self.name = name
        self.battle_model = battle_model

        cls = type(self)
        if not hasattr(cls, "_counter"):
            cls._counter = 0

        cls._counter += 1
        self.instance_id = cls._counter
        

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
        return f"{self.name}#{self.instance_id}"

class Daft(General):
    def __init__(self, battle_model):
        super().__init__("Daft", battle_model)

    def decide(self) -> None:
        my_units = self.battle_model.get_army(self)
        enemy_units = self.battle_model.get_enemy_army(self)

        if not enemy_units:
            return

        for unit in my_units:
            if not unit.is_alive() or not isinstance(unit.order, Wait):
                continue

            closest_enemy = self.get_closest_enemy(unit, enemy_units)
            if closest_enemy is None:
                continue

            unit.order = Attack(unit, closest_enemy)


class BrainDead(General):
    """
    Un général qui ne donne aucun ordre, toute l'armée est en mode Defense donc les unités attaquent les ennemis dans leur portée.
    """
    def __init__(self, battle_model):
        super().__init__("BrainDead", battle_model)

    def decide(self) -> None:
        for unit in self.battle_model.get_army(self):
            unit.order = Defense(unit)


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
        return best_enemy

    def decide(self) -> None:
        enemies = self.battle_model.get_enemy_army(self)
        if not enemies:
            return

        for unit in self.battle_model.get_army(self):
            if not isinstance(unit.order, Wait):
                continue

            target = self.get_best_enemy(unit, enemies)
            if not target:
                unit.order = Wait(unit)
                continue

            if unit.name != "Knight":
                unit.order = Attack(unit, target)
                continue

            if self.manhattan(unit, target) <= 2:
                unit.order = Attack(unit, target)
            elif target.name == "Pikeman" and self.has_crossbow_support(unit):
                unit.order = Wait(unit)
            else:
                unit.order = Attack(unit, target)

class MoveTestGeneral(General):
    """
    Un général qui ordonne à chaque unité de se déplacer vers des coordonnées aléatoires sur la carte si elle est en attente.
    """
    def __init__(self, battle_model):
        super().__init__("MoveTestGeneral", battle_model)

    def decide(self) -> None:
        for unit in self.battle_model.get_army(self):
            if isinstance(unit, Unit) and unit.is_alive() and isinstance(unit.order, Wait):
                # pick random coords inside the map 
                new_x = random.randrange(0, self.battle_model.map_width)
                new_y = random.randrange(0, self.battle_model.map_height)

                unit.order = Move(unit, new_x, new_y)



class AttackTestGeneral(General):
    """
    Un général qui ordonne à chaque unité d'attaquer une unité ennemie aléatoire si elle est en attente.
    """
    def __init__(self, battle_model):
        super().__init__("AttackTestGeneral", battle_model)

    def decide(self) -> None:
        enemy_units = self.battle_model.get_enemy_army(self)
        
        for unit in self.battle_model.get_army(self):
            if unit.is_alive() and isinstance(unit.order, Wait):
                if enemy_units:
                    # choose a random enemy unit to attack
                    target = random.choice(tuple(enemy_units))
                    unit.order = Attack(unit, target)
                else:
                    unit.order = Wait(unit)

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
                    unit.order = Attack(unit, nearest)
                    # if dist2 <= 4: 
                    #     unit.order = Attack(unit, nearest)
                else :
                    for u in enemy_units :
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x , u.y, 2)
                    if not anyone :
                        unit.order = Attack(unit, nearest)
                    else :
                        unit.order = Move(unit, new_x, new_y)

            # Knights
            if isinstance(unit, Knight):
                if self.posx_last_pike != 0 and self.posy_last_pike != 0:
                    if self.dist_ht_2(unit.x, unit.y, self.posx_last_pike, self.posy_last_pike):
                        Wait(unit)
                        
                if abs(avg_x-unit.x) <= 3 and abs(avg_y-unit.y) <= 3:
                    unit.order = Attack(unit, nearest)
                else:
                    for u in enemy_units:
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x, u.y, 2)
                    if not anyone:
                        unit.order = Attack(unit, nearest)
                    else:
                        unit.order = Move(unit, new_x, new_y)

            #Crossbowman
            if isinstance(unit, Crossbowman):
                if abs(avg_x-unit.x) <=3 and abs(avg_y -unit.y) <= 3:
                    unit.order = Attack(unit, nearest)
                    # if dist2 <= 4: 
                    #     unit.order = Attack(unit, nearest)
                else :
                    for u in enemy_units :
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x , u.y, 2)
                    if not anyone :
                        unit.order = Attack(unit, nearest)
                    else :
                        unit.order = Move(unit, new_x, new_y)
            anyone = False


class RPSGeneral(General):
    """
    IA avec :
    - priorité de type (RPS : Pikeman attaque Knight attaque Crossbowman attaque Pikeman)
    - un score qui calcule = bonus RPS + bonus ennemi faible (HP bas)+ bonus ennemi dangereux (haut DPS / bonus_attacks)-pénalité distance (Manhattan)
    - prise en compte du range (unit.range) ensuite on attack ou on attend
    """
    TARGET_PREFS = {
        "Pikeman":      ["Knight", "Crossbowman", "Pikeman"],
        "Knight":       ["Crossbowman", "Pikeman", "Knight"],
        "Crossbowman":  ["Pikeman", "Knight", "Crossbowman"],
    }

    def __init__(self, battle_model):
        super().__init__("RPS", battle_model)

    # calcul du score

    def score_target(self, unit: Unit, enemy: Unit) -> float | None:
        if not enemy.is_alive():
            return None

        dist = self.manhattan(unit, enemy)
        score = 0.0
        #pénalité distance
        score -= dist * 2.0
        #bonus RPS (type préféré)
        prefs = self.TARGET_PREFS.get(unit.name, [])
        if enemy.name in prefs:
            rps_weight = len(prefs) - prefs.index(enemy.name)
            score += rps_weight * 10.0

        #bonus ennemi faible
        if enemy.max_hp > 0:
            hp_ratio = enemy.hp / enemy.max_hp
            score += (1.0 - hp_ratio) * 8.0  

        # bonus ennemi dangereux 
        score += enemy.attack * 0.5

        #bonus si notre type est dans ses bonus_attacks
        if unit.__class__ in enemy.bonus_attacks:
            score += enemy.bonus_attacks[unit.__class__] * 0.5

        return score
    
    #prendre le meilleur score pour l'attaquer
    def get_best_enemy(self, unit: Unit, enemies: list[Unit]) -> Unit | None:
        best = None
        best_score = None
        for e in enemies:
            s = self.score_target(unit, e)
            if s is None:
                continue
            if best_score is None or s > best_score:
                best_score = s
                best = e
        return best

    #déplacement

    def get_step_towards(self, unit: Unit, target: Unit) -> tuple[int, int] | None:
        """
        Utilise le mini-pathfinding de BattleModel pour obtenir la prochaine case.
        """
        start = (unit.x, unit.y)
        end = (target.x, target.y)
        nxt = self.battle_model.shortest_path(start, end)
        return nxt  # soit (nx, ny), soit None si bloqué

    #décision
    def decide(self) -> None:
        enemies = self.battle_model.get_enemy_army(self)
        if not enemies:
            return

        for unit in self.battle_model.get_army(self):
            if not unit.is_alive() or not isinstance(unit.order, Wait):
                continue

            target = self.get_best_enemy(unit, enemies)
            if target is None:
                unit.order = Wait(unit)
                continue

            dist = self.manhattan(unit, target)
            # range = unit.range (0 pour Pikeman / Knight, 5 pour Crossbowman)
            attack_range = max(1, unit.range) 
            # Si possible d'attaquer ce tour, on Attack, sinon on Move vers la cible
            if dist <= attack_range:
                unit.order = Attack(unit, target)
            else:
                step = self.get_step_towards(unit, target)
                if step is None:
                    # bloqué : on peut attendre ou faire autre chose
                    unit.order = Wait(unit)
                else:
                    nx, ny = step
                    unit.order = Move(unit, nx, ny)


def generalFactory(general_type: str, battle_model) -> General:
    general_classes = {
        "daft": Daft,
        "braindead": BrainDead,
        "aegis": Aegis,
        "movetest": MoveTestGeneral,
        "attacktest": AttackTestGeneral,
        "momoia": MomoIA,
        "rps": RPSGeneral,
    }
    key = general_type.lower()
    if key in general_classes:
        return general_classes[key](battle_model)
    else:
        raise ValueError(f"Unknown general type: {key}")


