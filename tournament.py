from pathlib import Path
from pyexpat import model
from jinja2 import Environment, FileSystemLoader
from models.battle_model import BattleModel
from controllers.battle_controller import BattleController
from battle import Battle
from concurrent.futures import ProcessPoolExecutor, as_completed
from utils import ensure_key
from models.general import GeneralId

def run_single_battle_wrapper(args):
    gid1, gen_cls1, gid2, gen_cls2, scenario_path = args

    model = BattleModel()
    controller = BattleController(model, enable_input=False)

    gen1 = gen_cls1(model)
    gen2 = gen_cls2(model)

    battle = Battle(
        gen1,
        gen2,
        scenario_path,
        model=model,
        controller=controller,
    )

    winner = battle.run()

    if winner is None:
        winner_gid = None
    elif winner is gen1:
        winner_gid = gid1
    else:
        winner_gid = gid2

    return gid1, gid2, scenario_path, winner_gid


class Tournament:
    def __init__(self, generals, scenarios, number_of_rounds, model, controller):
        self.generals = []
        counter = {}

        for gen_cls in generals:
            counter.setdefault(gen_cls.__name__, 0)
            counter[gen_cls.__name__] += 1
            gid = GeneralId(gen_cls.__name__, counter[gen_cls.__name__])
            self.generals.append((gid, gen_cls))

        self.scenarios = scenarios
        self.number_of_rounds = number_of_rounds
        self.model = model
        self.controller = controller

        self.score_global = {}                    # general -> victoires totales
        self.matrix_gvg = {}                      # general1 -> general2 -> victoires
        self.matrix_by_scenario = {}              # scenario -> general1 -> general2 -> victoires
        self.score_general_vs_scenario = {}       # scenario -> general -> victoires
    
    def _update_scores(self, g1, g2, scenario, winner):
        # DRAW 
        if winner is None:
            return

        # SCORE GLOBAL
        ensure_key(self.score_global, winner, 0)
        self.score_global[winner] += 1

        # GvG MATRIX
        ensure_key(self.matrix_gvg, g1, {})
        ensure_key(self.matrix_gvg[g1], g2, 0)

        ensure_key(self.matrix_gvg, g2, {})
        ensure_key(self.matrix_gvg[g2], g1, 0)

        if winner == g1:
            self.matrix_gvg[g1][g2] += 1
        elif winner == g2:
            self.matrix_gvg[g2][g1] += 1

        # SCENARIO MATRIX
        s = ensure_key(self.matrix_by_scenario, scenario, {})

        ensure_key(s, g1, {})
        ensure_key(s, g2, {})

        ensure_key(s[g1], g2, 0)
        ensure_key(s[g2], g1, 0)

        if winner == g1:
            s[g1][g2] += 1
        else:
            s[g2][g1] += 1

        # GENERAL vs SCENARIO
        sg = ensure_key(self.score_general_vs_scenario, scenario, {})
        ensure_key(sg, winner, 0)
        sg[winner] += 1

    def run_sequential(self):
        print("Sequential tournament started")

        for scenario in self.scenarios:
            for i in range(len(self.generals)):
                for j in range(i + 1, len(self.generals)):
                    gid1, gen_cls1 = self.generals[i]
                    gid2, gen_cls2 = self.generals[j]

                    for r in range(self.number_of_rounds):
                        # alterner les positions

                        gen1 = gen_cls1(self.model)
                        gen2 = gen_cls2(self.model)

                        if r % 2 == 0:
                            pass
                        else:
                            gen1, gen2 = gen2, gen1
                            gid1, gid2 = gid2, gid1

                        battle = Battle(
                            gen1,
                            gen2,
                            scenario,
                            model=self.model,
                            controller=self.controller,
                        )

                        winner = battle.run()

                        if winner is None:
                            winner_gid = None
                        elif winner is gen1:
                            winner_gid = gid1
                        else:
                            winner_gid = gid2

                        self._update_scores(gid1, gid2, scenario, winner_gid)
                       

        print("All battles completed (sequential)")
        self.generate_html()


    def run_parallelized(self):
        tasks = []

        for scenario in self.scenarios:
            for i in range(len(self.generals)):
                for j in range(i + 1, len(self.generals)):
                    gid1, gen_cls1 = self.generals[i]
                    gid2, gen_cls2 = self.generals[j]

                    for r in range(self.number_of_rounds):
                        # alterner les positions
                        if r % 2 == 0:
                            tasks.append((gid1, gen_cls1, gid2, gen_cls2, scenario))
                        else:
                            tasks.append((gid2, gen_cls2, gid1, gen_cls1, scenario))

        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(run_single_battle_wrapper, t) for t in tasks]

            for f in as_completed(futures):
                gid1, gid2, scenario, winner = f.result()
                print(winner)
                self._update_scores(gid1, gid2, scenario, winner)
                print(f"Completed battle: {gid1} vs {gid2} on {scenario} - Winner: {winner}")


        print("All battles completed. (parallelized)")
        self.generate_html()


    def run(self):
        if len(self.controller.view_list) > 0:
            print("View detected : sequential mode")
            return self.run_sequential()
        print("No view detected : parallelized mode")
        return self.run_parallelized()


    def generate_html(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template("tournament.html")

        general_ids = [gid for gid, _ in self.generals]

        html = template.render(
            generals=general_ids,  
            scenarios=self.scenarios,
            score_global=self.score_global,
            matrix_gvg=self.matrix_gvg,
            matrix_by_scenario=self.matrix_by_scenario,
            score_general_vs_scenario=self.score_general_vs_scenario,
            rounds=self.number_of_rounds
        )

        out = Path("tournament_results.html")
        out.write_text(html, encoding="utf-8")
