import json

from models.general import generalFactory
from models.unit import unitFactory
from models.unit import *
from models.order import *
from models.general import *
from models.obstacle import *
from utils import bfs_path


class BattleModel:
    def __init__(self)->None:
        self.general_1 = None
        self.general_2 = None
        self.running = False
        self.map_width = None
        self.map_height = None
        self.list_objects = []


    def load(self, path:str, ai1:str, ai2:str)->None:
        # load json

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # load map

        map_data = data["map"]
        self.map_width = map_data["width"]
        self.map_height = map_data["height"]

        # load generals

        self.general_1 = generalFactory(ai1)
        self.general_2 = generalFactory(ai2)

        # load army
        army_data = data["armies"]
        for unit_data in army_data["army1"]:
            unit = unitFactory(
                unit_type=unit_data["type"],
                general=self.general_1,
                x=unit_data["x"],
                y=unit_data["y"]
            )
            self.general_1.my_units.append(unit)
            self.list_objects.append(unit)

        for unit_data in army_data["army2"]:
            unit = unitFactory(
                unit_type=unit_data["type"],
                general=self.general_2,
                x=unit_data["x"],
                y=unit_data["y"]
            )
            self.general_2.my_units.append(unit)
            self.list_objects.append(unit)

        print(f"BattleModel loaded: Map {self.map_width}x{self.map_height}, General 1: {self.general_1.name} with {len(self.general_1.my_units)} units, General 2: {self.general_2.name} with {len(self.general_2.my_units)} units.")

    def update(self) -> None:
        for unit in self.list_objects:
            isinstance(unit, Unit) and unit.action.action(self)

    def pause(self)->None:
        self.running = not self.running

    def save(self, scenario_file:str)->None:
        pass

