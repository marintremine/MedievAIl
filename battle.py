from controllers.battle_controller import BattleController
from models.battle_model import BattleModel

class Battle:
    def __init__(self, general_1, general_2, scenario, model=None, controller=None,):
        self.model = model

        self.general_1 = general_1
        self.general_2 = general_2
        self.scenario = scenario

        self.model = model
        self.controller = controller
        
        if model is None:
            self.model = BattleModel()
        if controller is None:
            self.controller = BattleController(self.model)
        

    def run(self):
        self.model.load(self.scenario, self.general_1, self.general_2)
        for v in self.controller.view_list:
            v.load()
        winnner = self.controller.run() if len(self.controller.view_list) > 0 else self.controller.run_fast()
        if winnner is not None:
            print(f"The winner is: {winnner.name} with {len(self.model.get_army(winnner))} units remaining.")
        else:
            print("The battle ended in a draw.")
        return winnner
    