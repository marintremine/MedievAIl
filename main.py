
import argparse
import sys

from controllers.battle_controller import BattleController
from controllers.live_server import start_flask_debug_server
from models.battle_model import BattleModel
from models.general import generalFactory

from views.pygame_view import PygameView
from views.terminal_view import TerminalView
from utils import *

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
        cli_battle(args)
    elif args.command == "tourney":
        cli_tournament(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()