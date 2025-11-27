
import argparse
import sys

from controllers.battle_controller import BattleController
from controllers.live_server import start_flask_debug_server
from models.battle_model import BattleModel
from views.pygame_view import PygameView
from views.terminal_view import TerminalView



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
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()