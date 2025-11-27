
import argparse
import sys
from pathlib import Path

from controllers.battle_controller import BattleController
from controllers.live_server import start_flask_debug_server
from models.battle_model import BattleModel
from views.pygame_view import PygameView
from views.terminal_view import TerminalView
from tourney import Tournament


def main():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="MedievAIl Battle Simulator (2025-2026)"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- RUN ----
    run_parser = subparsers.add_parser("run", help="Lancer une bataille")
    run_parser.add_argument("scenario", type=str, help="Chemin du scénario à exécuter")
    run_parser.add_argument("ai1", type=str, help="Nom du premier AI (general)")
    run_parser.add_argument("ai2", type=str, help="Nom du second AI (general)") 
    run_parser.add_argument("-t", "--terminal", action="store_true", help="Afficher la vue terminal")
    run_parser.add_argument("-d", "--datafile", type=str, default=None,
                            help="Chemin du fichier pour écrire les données de la bataille (ou '-' pour stdout)")
    
    # ---- TOURNEY ----
    tourney_parser = subparsers.add_parser("tourney", help="Lancer un tournoi entre plusieurs IA")
    tourney_parser.add_argument("-G", "--generals", nargs='+', required=True,
                                help="Liste des IA (généraux) à inclure dans le tournoi")
    tourney_parser.add_argument("-S", "--scenarios", nargs='+', required=True,
                                help="Liste des scénarios à exécuter (chemins)")
    tourney_parser.add_argument("-N", "--num", type=int, default=10,
                                help="Nombre de batailles par paire (défaut: 10)")
    tourney_parser.add_argument("-d", "--datafile", type=str, default=None,
                                help="Chemin du fichier pour écrire les résultats (ou '-' pour stdout)")


    args = parser.parse_args()

    if args.command == "run":
        model = BattleModel()
        model.load(args.scenario, args.ai1, args.ai2)
        controller = BattleController(model, None)
        controller.datafile = args.datafile

        if args.terminal:
            view = TerminalView(model, controller)
        else:
            view = PygameView(model, controller)
        controller.view = view

        start_flask_debug_server(model)
        controller.run()
    elif args.command == "tourney":
        print("Generals:", args.generals)
        print("Scenarios:", args.scenarios)
        # print("Number of battles per pair:", args.num)
        tournament = Tournament(args.generals, args.scenarios)
        tournament.run()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()