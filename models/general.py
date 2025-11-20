from __future__ import annotations
import random

from models.order import Move, Wait

class General:
    def __init__(self, name: str,  my_units: list["Unit"], battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        self.name = name
        self.my_units = my_units
        self.battle_model = battle_model

    def decide(self) -> None:
        pass


class Daft(General):
    def __init__(self, battle_model):
        super().__init__("Daft", [], battle_model)
    def decide(self) -> None:
        pass

class BrainDead(General):
    def __init__(self, battle_model):
        super().__init__("BrainDead", [], battle_model)

    def decide(self) -> None:
        pass

class TestGeneral(General):
    def __init__(self, battle_model):
        super().__init__("TestGeneral", [], battle_model)

    def decide(self) -> None:
        for unit in self.my_units:
            if unit.is_alive() and isinstance(unit.action, Wait):
                # pick random coords inside the map 
                new_x = random.randrange(0, self.battle_model.map_width)
                new_y = random.randrange(0, self.battle_model.map_height)

                unit.action = Move(unit, new_x, new_y, self.battle_model)


def generalFactory(general_type: str, battle_model) -> General:
    general_classes = {
        "daft": Daft,
        "braindead": BrainDead,
        "test": TestGeneral
    }
    key = general_type.lower()
    if key in general_classes:
        return general_classes[key](battle_model)
    else:
        raise ValueError(f"Unknown general type: {key}")