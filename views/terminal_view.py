from time import time
from views.battle_view import BattleView
from models.battle_model import BattleModel
from models.unit import *
import curses

class TerminalView(BattleView):
    def __init__(self, model, controller):
        super().__init__(model, controller)
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0) # Masquer le curseur
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True) # Non-bloquant pour les inputs
        
        # Initialiser les couleurs
        curses.start_color()
        curses.use_default_colors()
        
        # Définir les paires de couleurs
        curses.init_pair(1, curses.COLOR_RED, -1) # Général 1
        curses.init_pair(2, curses.COLOR_BLUE, -1) # Général 2
        curses.init_pair(3, curses.COLOR_WHITE, -1) # Terrain
        
        # Mapper les généraux aux couleurs
        self.general_colors = {
            self.model.general_1: 1,
            self.model.general_2: 2
        }
        
        # Cache pour éviter les redessins inutiles
        self.last_state = None
    
    def render(self) -> None:
        """Affiche la carte, les unités et obstacles en mode texte."""
        
        # Récupérer les dimensions
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Effacer seulement ce qui a changé au lieu de tout clear()
        # Ou utiliser erase() qui est plus rapide que clear()
        self.stdscr.erase()
        
        # Afficher la carte (terrain)
        for y in range(min(self.model.map_height, max_y)):
            for x in range(min(self.model.map_width, max_x)):
                if y == max_y - 1 and x == max_x - 1:
                    continue
                try:
                    self.stdscr.addch(y, x, '.', curses.color_pair(3))
                except curses.error:
                    pass
        
        # Afficher les unités avec leur couleur
        for obj in self.model.list_objects:
            if isinstance(obj, Unit) and not obj.is_alive():
                continue

            if 0 <= obj.y < max_y and 0 <= obj.x < max_x:
                if obj.y == max_y - 1 and obj.x == max_x - 1:
                    continue
                
                symbol = self._get_unit_symbol(obj)
                color_pair = self._get_unit_color(obj)
                
                try:
                    self.stdscr.addch(obj.y, obj.x, symbol, 
                                    curses.color_pair(color_pair) | curses.A_BOLD)
                except curses.error:
                    pass


        # --- Affichage des infos système / debug ---
        status_y = min(self.model.map_height + 1, max_y - 1)

        time_str = f"Temps : {time():.1f}s"
        running_str = "RUNNING" if self.model.running else "PAUSED"
        speed_str = f"Speed: {self.controller.game_speed}x"

        info_line = f"{time_str}   |   État : {running_str}   |   {speed_str}"

        try:
            self.stdscr.addstr(status_y, 0, info_line[:max_x - 1])
        except curses.error:
            pass

        
        # Rafraîchir l'écran une seule fois à la fin
        self.stdscr.refresh()
    
    
    def _get_unit_symbol(self, unit):
        """Définit un symbole simple pour représenter les unités."""
        if isinstance(unit, Knight):
            return "K"
        elif isinstance(unit, Pikeman):
            return "P"
        elif isinstance(unit, Crossbowman):
            return "C"
        return "U"
    
    def _get_unit_color(self, unit):
        """Retourne la couleur associée au général de l'unité."""
        if hasattr(unit, 'general') and unit.general in self.general_colors:
            return self.general_colors[unit.general]
        return 3
    
    def cleanup(self):
        """Restaure les paramètres du terminal."""
        curses.curs_set(1)
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()