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

    def move_view(self, x, y):
        pass

    def move_view_fast(self, x, y):
        pass

    def scroll_up(self):
        pass

    def scroll_down(self):
        pass

    def next_view_mode(self):
        pass

    def prev_view_mode(self):
        pass