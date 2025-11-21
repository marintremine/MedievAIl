from views.battle_view import BattleView
from models.battle_model import BattleModel

class PygameView(BattleView):
    def __init__(self, model , controller):
        super().__init__(model, controller)
        # Initialize Pygame here

    def render(self):
        pass

    def getInput(self):
        pass