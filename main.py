
import argparse
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from controllers.battle_controller import BattleController
from controllers.live_server import start_flask_debug_server
from models.general import General, generalFactory
from models.battle_model import BattleModel
from views.pygame_view import PygameView
from views.terminal_view import TerminalView
from utils import *

class Battle:
    def __init__(self, model, controller, general_1, general_2, scenario):
        self.model = model
        self.controller = controller
        self.general_1 = general_1
        self.general_2 = general_2
        self.scenario = scenario

    def run(self):
        self.model.reset()
        self.model.load(self.scenario, self.general_1, self.general_2)
        for v in self.controller.view_list:
            v.load()
        winner = None
        if len(self.controller.view_list) > 0:
            winner = self.controller.run()
        else:
            winner = self.controller.run_fast()
        return winner
    
class Tournament:
    def __init__(self, model , controller, generals, scenarios, number_of_rounds):
        self.model = model
        self.controller = controller
        self.generals = generals
        self.scenarios = scenarios
        self.number_of_rounds = number_of_rounds

        self.score_global = {}                    # general -> victoires totales
        self.matrix_gvg = {}                      # general1 -> general2 -> victoires
        self.matrix_by_scenario = {}              # scenario -> general1 -> general2 -> victoires
        self.score_general_vs_scenario = {}       # scenario -> general -> victoires

    def run(self):
        for scenario_path in self.scenarios:
            for i in range(len(self.generals)):
                for j in range(i + 1, len(self.generals)):
                    gen1 = self.generals[i]
                    gen2 = self.generals[j]
                    print(f"Starting matches between {gen1} and {gen2} on scenario {scenario_path}")
                    for r in range(self.number_of_rounds):
                        # alterne les positions
                        if r % 2 == 0:
                            general_1, general_2 = gen1, gen2
                        else:
                            general_1, general_2 = gen2, gen1

                        battle = Battle(self.model, self.controller, general_1, general_2, scenario_path)
                        winner = battle.run()

                        print("Winner:", winner)

                        if winner is None:
                            print(f"Round {r + 1}/{self.number_of_rounds}: Draw")
                            continue  # match nul

                        print(f'Round {r + 1}/{self.number_of_rounds}: Winner is {winner}')

                        # Met à jour les scores
                        
                        # score global
                        ensure_key(self.score_global, winner, 0)
                        self.score_global[winner] += 1

                        # matrice générale
                        ensure_key(self.matrix_gvg, gen1, {})
                        ensure_key(self.matrix_gvg[gen1], gen2, 0)
                        if winner == gen1:
                            self.matrix_gvg[gen1][gen2] += 1

                        ensure_key(self.matrix_gvg, gen2, {})
                        ensure_key(self.matrix_gvg[gen2], gen1, 0)
                        if winner == gen2:
                            self.matrix_gvg[gen2][gen1] += 1

                        # matrice par scénario
                        s = ensure_key(self.matrix_by_scenario, scenario_path, {})
                        row = ensure_key(s, gen1, {})
                        ensure_key(row, gen2, 0)
                        if winner == gen1:
                            row[gen2] += 1

                        row2 = ensure_key(s, gen2, {})
                        ensure_key(row2, gen1, 0)
                        if winner == gen2:
                            row2[gen1] += 1

                        # score général vs scénario
                        sg = ensure_key(self.score_general_vs_scenario, scenario_path, {})
                        ensure_key(sg, winner, 0)
                        sg[winner] += 1
                        

        print("Tournament completed.")
        self.generate_html()

    def generate_html(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template("tournament.html")

        html = template.render(
            generals=self.generals,
            scenarios=self.scenarios,
            score_global=self.score_global,
            matrix_gvg=self.matrix_gvg,
            matrix_by_scenario=self.matrix_by_scenario,
            score_general_vs_scenario=self.score_general_vs_scenario,
            rounds=self.number_of_rounds
        )
        print("html")
        out = Path("tournament_results.html")
        out.write_text(html, encoding="utf-8")
        print(f"HTML results generated → {out.absolute()}")

def main():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="MedievAIl Battle Simulator (2025-2026)"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- BATTLE ----
    battle_parser = subparsers.add_parser("battle", help="Lancer une bataille")
    battle_parser.add_argument("scenario", type=str, help="Chemin du scénario à exécuter")
    battle_parser.add_argument("ai1", type=str, help="Nom du premier AI (general)")
    battle_parser.add_argument("ai2", type=str, help="Nom du second AI (general)") 
    battle_parser.add_argument("-t", "--terminal", action="store_true", help="Afficher la vue terminal")
    battle_parser.add_argument("-p", "--pygame", action="store_true",
                            help="Utiliser la vue pygame pour la bataille")
    battle_parser.add_argument("-d", "--datafile", type=str, default=None,
                            help="Chemin du fichier pour écrire les données de la bataille (ou '-' pour stdout)")
    
    # ---- TOURNEY ----
    tourney_parser = subparsers.add_parser("tourney", help="Lancer un tournoi entre plusieurs IA et différents scénarios")
    tourney_parser.add_argument("-G", "--generals", nargs='+', required=True,
                                help="Liste des IA (généraux) à inclure dans le tournoi")
    tourney_parser.add_argument("-S", "--scenarios", nargs='+', required=True,
                                help="Liste des scénarios à exécuter (chemins)")
    tourney_parser.add_argument("-N", "--num", type=int, default=10,
                                help="Nombre de batailles par paire (défaut: 10)")
    tourney_parser.add_argument("-d", "--datafile", type=str, default=None,
                                help="Chemin du fichier pour écrire les résultats (ou '-' pour stdout)")
    tourney_parser.add_argument("-t", "--terminal", action="store_true",
                                help="Utiliser la vue terminal pour le tournoi")
    tourney_parser.add_argument("-p", "--pygame", action="store_true",
                                help="Utiliser la vue pygame pour le tournoi")

    args = parser.parse_args()

    if args.command == "battle":
        # Setup model, controller, view
        model = BattleModel()
        controller = BattleController(model)
        controller.datafile = args.datafile

        if args.terminal:
            view = TerminalView(model, controller)
            controller.view_list.append(view)
        elif args.pygame:
            view = PygameView(model, controller)
            controller.view_list.append(view)

        # Run battle
        if len(controller.view_list) > 0:
            start_flask_debug_server(model)

        general_1 = generalFactory(args.ai1, model)
        general_2 = generalFactory(args.ai2, model)

        battle = Battle(model, controller, general_1=general_1, general_2=general_2, scenario=args.scenario)
        winner = battle.run()
        if winner:
            print(f"The winner is: {winner.name}")
        else:
            print("The battle ended in a draw.")
    elif args.command == "tourney":
        # Setup model, controller, view
        model = BattleModel()
        controller = BattleController(model)
        controller.datafile = args.datafile

        if args.terminal:
            view = TerminalView(model, controller)
            controller.view_list.append(view)
        elif args.pygame:
            view = PygameView(model, controller)
            controller.view_list.append(view)

        generals = [generalFactory(name, model) for name in args.generals]

        # Run tournament
        tournament = Tournament(model, controller, generals, args.scenarios, number_of_rounds=args.num)
        tournament.run()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()