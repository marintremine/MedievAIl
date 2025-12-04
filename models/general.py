from __future__ import annotations
import random

from models.order import Attack, Move, Wait, Defense
from models.unit import Object, Unit

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
        ax, ay = a.x, a.y
        bx, by = (b if isinstance(b, tuple) else (b.x, b.y))
        return abs(ax - bx) + abs(ay - by)
    
    def weakest_targets(self, enemies):
        """Cherche les cibles faibles (<=30% HP) parmi les ennemis donnés."""
        return [e for e in enemies if e.is_alive() and e.hp <= e.max_hp * 0.3]
    
    def is_weak(self, unit):
        """Vérifie si une unité est faible (<=30% HP)."""
        return unit.is_alive() and unit.hp <= unit.max_hp * 0.3
    
    def is_close(self, unit, enemy, threshold=3):
        """Vérifie si une unité est proche d'un ennemi selon un seuil donné."""
        return self.manhattan(unit, enemy) <= threshold

    def decide(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.name}"

class Daft(General):
    """
    Major DAFT :
    - Toutes les unités attaquent systématiquement l’ennemi vivant le plus proche
    - Elles n'attendent pas d'avoir un ennemi en vue : elles se déplacent si nécessaire
    - Aucun calcul stratégique : pure agression
    """

    def __init__(self, battle_model):
        super().__init__("Daft", battle_model)

    def decide(self) -> None:
        enemy_army = self.battle_model.get_enemy_army(self)
        friendly_army = self.battle_model.get_army(self)

        if not enemy_army:
            return

        for unit in friendly_army:
            if not unit.is_alive():
                continue

            # On ne remplace pas un ordre d'attaque déjà en cours
            if isinstance(unit.action, Attack):
                continue

            # Trouver l'ennemi vivant le plus proche
            target = self.get_closest_enemy(unit, enemy_army)

            if target is None:
                unit.action = Wait(unit)
                continue

            # Toujours attaquer le plus proche (même s'il faut bouger pour l'atteindre)
            unit.action = Attack(unit, target)


class BrainDead(General):
    """
    Un général qui ne donne aucun ordre, toute l'armée est en mode Defense donc les unités attaquent les ennemis dans leur portée.
    """
    def __init__(self, battle_model):
        super().__init__("BrainDead", battle_model)

    def decide(self) -> None:
        enemy_army = self.battle_model.get_enemy_army(self)
        friendly_army = self.battle_model.get_army(self)

        for unit in friendly_army:
            if not unit.is_alive():
                continue

            if isinstance(unit.action, Attack):
                continue

            target = None
            for enemy in enemy_army:
                if enemy.is_alive() and unit.in_sight(enemy):
                    target = enemy
                    break

            if target is not None:
                unit.action = Attack(unit, target)
                continue

            if not isinstance(unit.action, Wait):
                unit.action = Wait(unit)


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

class IAValentin(General):
    def __init__(self, battle_model):
        super().__init__("IAValentin", battle_model)
        self.retreat_steps = 0
        self.max_retreat = 3

    def get_best_target(self, unit, enemies):
        """Détermine la meilleure cible ennemie en fonction de divers critères."""
        best_target = None
        best_score = None
        enemies_in_sight = [e for e in enemies if unit.in_sight(e)]
        weak = self.weakest_targets(enemies)

        for e in enemies:
            score = -(self.manhattan(unit, e))  # base = proximité

            # Bonus si ennemi en vue
            if e in enemies_in_sight:
                score += 2

            # Priorité aux unités faibles
            if e in weak:
                score += 4

            # --- Bonus / Malus selon matchup ---
            if unit.name == "Crossbowman":
                if e.name == "Knight":  # bonne cible
                    score += 5
                if e.name == "Pikeman":
                    score += 3
                # Malus si trop proche (danger)
                if self.manhattan(unit, e) <= 3:
                    score -= 6

            if unit.name == "Knight":
                if e.name == "Crossbowman":
                    score += 5
                if e.name == "Pikeman":
                    score -= 4  # éviter les piquiers !

            if unit.name == "Pikeman":
                if e.name == "Knight":
                    score += 5

            if best_score is None or score > best_score:
                best_score = score
                best_target = e

        return best_target

    def decide(self):
        """Prend des décisions pour chaque unité alliée en fonction de la situation."""
        enemies = self.battle_model.get_enemy_army(self)
        allies = self.battle_model.get_army(self)

        if not enemies:
            return

        for unit in allies:
            if not isinstance(unit.action, Wait):
                continue

            target = self.get_best_target(unit, enemies)
            if not target:
                unit.action = Wait(unit)
                continue

            unit.action = Attack(unit, target)

def generalFactory(general_type: str, battle_model) -> General:
    general_classes = {
        "daft": Daft,
        "braindead": BrainDead,
        "aegis": Aegis,
        "movetest": MoveTestGeneral,
        "attacktest": AttackTestGeneral,
        "iaval": IAValentin
    }
    key = general_type.lower()
    if key in general_classes:
        return general_classes[key](battle_model)
    else:
        raise ValueError(f"Unknown general type: {key}")