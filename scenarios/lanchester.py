from models.battle_model import BattleModel
from models.unit import Pikeman, Crossbowman, Knight
from models.general import generalFactory


class LanchesterScenario:
    def __init__(self, model):
        self.model = model

    def setup(self, unit_type_name, N, ai_name):
        """
        Configure la bataille N vs 2N en utilisant l'IA spécifiée.
        """
        self.model.map_width = 100
        self.model.map_height = 100
        self.model.general_1 = generalFactory(ai_name, self.model)
        self.model.general_2 = generalFactory(ai_name, self.model)
        self.model.objects['units'].clear()
        self.model.objects['armies'][self.model.general_1] = set()
        self.model.objects['armies'][self.model.general_2] = set()

        unit_map = {
            "Pikeman": Pikeman,
            "Knight": Knight,
            "Crossbowman": Crossbowman
        }

        if unit_type_name not in unit_map:
            raise ValueError(f"Type d'unité inconnu: {unit_type_name}")

        unit_cls = unit_map[unit_type_name]
        y_pos_1 = 45
        y_pos_2 = 46
        if unit_type_name == "Crossbowman":
            y_pos_2 = 52
        for i in range(N):
            u = unit_cls(self.model.general_1, x=i % 100, y=y_pos_1 + (i // 100), battle_model=self.model)
            self.model.objects['units'].add(u)
            self.model.objects['armies'][self.model.general_1].add(u)
        for i in range(N * 2):
            u = unit_cls(self.model.general_2, x=i % 100, y=y_pos_2 + (i // 100), battle_model=self.model)
            self.model.objects['units'].add(u)
            self.model.objects['armies'][self.model.general_2].add(u)