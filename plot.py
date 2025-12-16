import os
import re
import time
import matplotlib.pyplot as plt
from datetime import datetime
from settings import MAX_TICK
from math import sqrt
from scenarios.lanchester import LanchesterScenario

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