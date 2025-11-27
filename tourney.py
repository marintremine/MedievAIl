from controllers.battle_controller import BattleController
from models.battle_model import BattleModel
from views.terminal_view import TerminalView


DEFAULT_MAX_TICKS = 5000

class Tournament:
    def __init__(self, generals, scenarios):
        self.generals = generals
        self.scenarios = scenarios
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
                    print(f"Running battles between {gen1} and {gen2} on scenario {scenario_path}")
                    model.load(scenario_path, gen1, gen2)
                    controller.run()
                    if model.winner != None:
                        winner = model.winner
                        print(f"Winner: {winner}")
                        # self.results[winner] += 1


        print("Tournament completed.")
        print("Results:")
        for gen, score in self.results.items():
            print(f"{gen}: {score} points")