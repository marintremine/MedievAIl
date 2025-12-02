from models.battle_model import BattleModel

class BattleView:
    def __init__(self,  model, controller):
        self.model = model
        self.controller = controller

    def render(self):
        pass

    def getInput(self):
        pass

    def cleanup(self):
        pass