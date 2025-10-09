
import argparse
import sys

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

    args = parser.parse_args()

    if args.command == "run":
        print(f"Lancement de la bataille avec le scénario : {args.scenario}, AI1 : {args.ai1}, AI2 : {args.ai2}, Terminal : {args.terminal}")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()