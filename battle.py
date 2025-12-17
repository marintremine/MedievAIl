import sys
from controllers.battle_controller import BattleController
from models.battle_model import BattleModel
from utils import LIST_UNITS_TYPES

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

        winner = self.controller.run() if len(self.controller.view_list) > 0 else self.controller.run_fast()

        original_stdout = sys.stdout
        if hasattr(self.controller, 'shared_log_buffer'):
            sys.stdout = self.controller.shared_log_buffer

        try:
            if winner is not None:
                winner_survivors = self.model.summary()
                print(f"The winner is: {winner.name} with {len(self.model.get_army(winner))} units remaining.")
                parts = [f"{winner_survivors[t]} {t}" for t in LIST_UNITS_TYPES]
                if len(parts) == 1:
                    summary = parts[0]
                else:
                    summary = ", ".join(parts[:-1]) + f" and {parts[-1]}"
                print(f"{winner.name} had {summary} remaining.")
            else:
                print("The battle ended in a draw.")
        finally:
            sys.stdout = original_stdout