import time

from models.battle_model import BattleModel
from views.battle_view import BattleView

class BattleController:
    def __init__(self, model : BattleModel, view : BattleView, tick_speed : int):
        self.model = model
        self.view = view
        self.tick_speed = tick_speed

    def run(self):
        pass

    