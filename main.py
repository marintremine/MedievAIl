import argparse
import os
import re
import sys
import time
from datetime import datetime
from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader

from controllers.battle_controller import BattleController
from controllers.live_server import start_flask_debug_server
from models.battle_model import BattleModel
from models.general import General, generalFactory
from scenarios.lanchester import LanchesterScenario
from settings import MAX_TICK
from utils import *
from models.general import generalFactory

from views.pygame_view import PygameView
from views.terminal_view import TerminalView

from battle import Battle
from tournament import Tournament


def cli_battle(args):
    """Exécution du mode battle (un seul combat)."""

    model = BattleModel()
    controller = BattleController(model)
    controller.datafile = args.datafile

    if args.terminal:
        view = TerminalView(model, controller)
        controller.view_list.append(view)
    if args.pygame:
        view = PygameView(model, controller)
        controller.view_list.append(view)

    # si vue, démarrer le serveur Flask pour le débogage
    if len(controller.view_list) > 0:
        start_flask_debug_server(model)

    # création des généraux
    general_1 = generalFactory(args.ai1, model)
    general_2 = generalFactory(args.ai2, model)

    # Exécuter le combat
    battle = Battle(general_1, general_2, args.scenario,
                    model=model, controller=controller)

    winner = battle.run()

    if winner:
        print(f"The winner is: {winner.name}")
    else:
        print("The battle ended in a draw.")


def cli_tournament(args):
    """Exécution du tournoi complet."""

    model = BattleModel()
    controller = BattleController(model)
    controller.datafile = args.datafile

    if args.terminal:
        view = TerminalView(model, controller)
        controller.view_list.append(view)
    if args.pygame:
        view = PygameView(model, controller)
        controller.view_list.append(view)

    # création des généraux
    generals = [ generalFactory(g, model).__class__ for g in args.generals ]

    # créer et lancer le tournoi
    tournament = Tournament(
        model=model,
        controller=controller,
        generals=generals,
        scenarios=args.scenarios,
        number_of_rounds=args.num,
    )

    tournament.run()


class Plot:
    def __init__(self, model, controller, args):
        self.model = model
        self.controller = controller
        self.ai_name = args.ai
        self.plotter_name = args.plotter
        self.scenario_name = args.scenario_args[0]
        self.raw_args = "".join(args.scenario_args[1:])
        self.num_runs = args.num
        self.controller.datafile = args.datafile

    def run(self):
        print(f"--- Démarrage du traçage : {self.scenario_name} ---")

        params = self.parse()
        if not params:
            return

        if self.scenario_name == "Lanchester":
            results = self.lanchester_simulation(params)
            if self.plotter_name == "PlotLanchester":
                self.lanchester_plotting(results)
            else:
                print(f"Plotter inconnu : {self.plotter_name}")
        else:
            print(f"Scénario non supporté pour le plot : {self.scenario_name}")

    def parse(self):
        types_match = re.search(r"\[(.*?)\]", self.raw_args)
        range_match = re.search(r"range\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", self.raw_args)

        if not types_match or not range_match:
            print(f"Erreur de format arguments. Format attendu : {self.scenario_name} \"[Type1,Type2]\" \"range(Début,Fin)\"")
            return None
        raw_types = types_match.group(1)
        unit_types = [t.strip() for t in raw_types.split(',')]
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        n_range = range(start, end)
        return {"types": unit_types, "range": n_range}

    def lanchester_simulation(self, params):
        results = {}
        for unit in params["types"]:
            results[unit] = {'x': [], 'y': []}
            print(f"Simulation de {unit}")

            for N in params["range"]:
                if N <= 0: continue
                total_survivors = 0
                for _ in range(self.num_runs):
                    self.model.reset()
                    LanchesterScenario(self.model).setup(unit, N, self.ai_name)
                    self.model.running = True
                    tick_count = 0

                    while tick_count < MAX_TICK and self.model.winner is None:
                        time.sleep(0.0001)
                        self.model.delta_time = 1
                        self.model.update()
                        tick_count += 1

                    if tick_count >= MAX_TICK:
                        self.model.running = False

                    survivors = len(self.model.get_army(self.model.general_2))
                    total_survivors += survivors

                avg_survivors = total_survivors / self.num_runs
                results[unit]['x'].append(N)
                results[unit]['y'].append(avg_survivors)
        return results

    def lanchester_plotting(self, results):
        plt.figure(figsize=(10, 6))

        for u_type, data in results.items():
            x_vals = data['x']

            # On défini un label et une couleur pour chaque unité
            if u_type == "Pikeman":
                y_theo = x_vals
                theory_label = f"Loi Linéaire - Théorie (y=N)"
                color_theo = 'lightcoral'
                color_simu = 'darkred'
                line_style_simu = '^-'
            elif u_type == "Knight":
                y_theo = x_vals
                theory_label = f"Loi Linéaire - Théorie (y=N)"
                color_theo = 'lightgreen'
                color_simu = 'darkgreen'
                line_style_simu = 's-'
            elif u_type == "Crossbowman":
                y_theo = [n * sqrt(3) for n in x_vals]
                theory_label = f"Loi Carrée - Théorie (y=$\\sqrt{{3}}$N)"
                color_theo = 'cornflowerblue'
                color_simu = 'darkblue'
                line_style_simu = 'o-'
            else:
                y_theo = []
                theory_label = "Théorie Inconnue"
                color_theo = 'gray'
                color_simu = 'black'
                line_style_simu = 'x-'


            theo_curve_label = f"Théorie ({u_type}): {theory_label}"
            current_labels = [line.get_label() for line in plt.gca().get_lines()]

            if theory_label not in current_labels:
                plt.plot(x_vals, y_theo, '--', alpha=0.6, color=color_theo, label=theory_label, linewidth=1.5)

            plt.plot(data['x'], data['y'], line_style_simu, label=f"{u_type} (Simu {self.ai_name})",
                     color=color_simu, linewidth=3, markersize=5)

        plt.title(f"Lois de Lanchester : Survivants Armée Forte (2N) vs N")
        plt.xlabel("Taille Armée Faible (N)")
        plt.ylabel(f"Survivants Armée Forte (2N) - Moyenne sur {self.num_runs} essais")
        plt.legend()
        plt.grid(True)

        output_dir = "simulations"
        os.makedirs(output_dir, exist_ok=True)

        if self.controller.datafile:
            filename = self.controller.datafile
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"lanchester_plot_{timestamp}.png")

        plt.savefig(filename)
        print(f"Graphique sauvegardé sous : {filename}")

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

    # ---- PLOT ----
    plot_parser = subparsers.add_parser("plot",
                                        help="Effectuer un traçages des pertes durant une bataille ou une série de batailles")
    plot_parser.add_argument("ai", type=str, help="Nom de l'AI (general) à utiliser pour le test du scénario")
    plot_parser.add_argument("plotter", type=str,
                             help="Nom de la fonction ou classe 'Plotter' à utiliser pour générer le graphique")
    plot_parser.add_argument("scenario_args", nargs='+', type=str,
                             help="Nom du scénario suivi de ses arguments (ex: Lanchester [Knight, Crossbow] range(1,100))")
    plot_parser.add_argument("-N", "--num", type=int, default=10,
                             help="Nombre de batailles par point de donnée pour la moyenne (défaut: 10)")
    plot_parser.add_argument("-d", "--datafile", type=str, default=None,
                             help="Chemin du fichier pour écrire les données brutes générées par le scénario")


    args = parser.parse_args()

    if args.command == "battle":
        cli_battle(args)
    elif args.command == "tourney":
        cli_tournament(args)
    elif args.command == "plot":
        model = BattleModel()
        controller = BattleController(model)
        controller.datafile = args.datafile
        plot_session = Plot(model, controller, args)
        plot_session.run()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()