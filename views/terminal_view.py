from views.battle_view import BattleView
from models.battle_model import BattleModel

class TerminalView(BattleView):
    def __init__(self, model : BattleModel):
        super().__init__(model)
        # Initialize Terminal here

    def render(self):
        pass

    def getInput(self):
        pass