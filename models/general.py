from __future__ import annotations
import random

from models.order import Attack, Move, Wait
from models.unit import Unit

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
    def __init__(self, battle_model):
        super().__init__("MoveTestGeneral", battle_model)

    def decide(self) -> None:
        for unit in self.battle_model.get_army(self):
            if isinstance(unit, Unit) and unit.is_alive() and isinstance(unit.action, Wait):
                # pick random coords inside the map 
                new_x = random.randrange(0, self.battle_model.map_width)
                new_y = random.randrange(0, self.battle_model.map_height)

                unit.action = Move(unit, new_x, new_y, self.battle_model)

class AttackTestGeneral(General):
    def __init__(self, battle_model):
        super().__init__("AttackTestGeneral", battle_model)

    def decide(self) -> None:
        enemy_units = self.battle_model.get_enemy_army(self)
        for unit in self.battle_model.get_army(self):
            if unit.is_alive() and isinstance(unit.action, Wait):
                if enemy_units:
                    # choose a random enemy unit to attack
                    target = random.choice(enemy_units)
                    unit.action = Attack(unit, target, self.battle_model)
                else:
                    unit.action = Wait(unit)


def generalFactory(general_type: str, battle_model) -> General:
    general_classes = {
        "daft": Daft,
        "braindead": BrainDead,
        "movetest": MoveTestGeneral,
        "attacktest": AttackTestGeneral
    }
    key = general_type.lower()
    if key in general_classes:
        return general_classes[key](battle_model)
    else:
        raise ValueError(f"Unknown general type: {key}")