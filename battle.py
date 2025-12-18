import sys, io
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
        original_stdout = sys.stdout

        # Détection pour activer la capture
        has_terminal_view = any(v.__class__.__name__ == 'TerminalView' for v in self.controller.view_list)
        has_buffer = hasattr(self.controller, 'shared_log_buffer')
        should_capture = has_terminal_view and has_buffer

        if should_capture:
            sys.stdout = self.controller.shared_log_buffer


        try:
            self.model.load(self.scenario, self.general_1, self.general_2)
            
            for v in self.controller.view_list:
                v.load()

            winner = self.controller.run() if len(self.controller.view_list) > 0 else self.controller.run_fast()

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
            # On restaure la sortie standard (pour que le prochain print aille dans le terminal Linux)
            sys.stdout = original_stdout

            # On demande à la vue d'afficher ce qu'elle a retenu
            for v in self.controller.view_list:
                if hasattr(v, 'flush_logs'):
                    v.flush_logs()

        return winner