from controllers.battle_controller import BattleController
from models.battle_model import BattleModel
from views.terminal_view import TerminalView

class Tournament:
    def __init__(self, generals, scenarios):
        self.generals = generals
        self.scenarios = scenarios
        self.number_of_rounds = 1
        self.results = {gen: 0 for gen in generals} 

    def run(self):
        model = BattleModel()
        controller = BattleController(model, None)
        view = TerminalView(model, controller)
        controller.view = view
        
        for scenario_path in self.scenarios:
            for i in range(len(self.generals)):
                for j in range(i + 1, len(self.generals)):
                    gen1 = self.generals[i]
                    gen2 = self.generals[j]
                    for round_num in range(self.number_of_rounds):
                        model.reset()
                        model.load(scenario_path, gen1, gen2)
                        print(f"Battle n°{round_num + 1}/{self.number_of_rounds} between {gen1} and {gen2} on scenario {scenario_path}")
                        winner = controller.run()
                        if winner:
                            print(f"Winner: {winner}")
                        else:
                            print("Draw")

        print("Tournament completed.")
        print("Results:")
        for gen, score in self.results.items():
            print(f"{gen}: {score} points")