from views.battle_view import BattleView
from models.battle_model import BattleModel
from models.unit import Knight
from models.unit import Pikeman
from models.unit import Crossbowman
import curses

class TerminalView(BattleView):
    def __init__(self, model: BattleModel):
        super().__init__(model)
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
        # Créer un snapshot de l'état actuel
        current_state = self._get_state_snapshot()
        
        # Ne redessiner que si l'état a changé
        if current_state == self.last_state:
            return
        
        self.last_state = current_state
        
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
        
        # Rafraîchir l'écran une seule fois à la fin
        self.stdscr.refresh()
    
    def _get_state_snapshot(self):
        """Crée un snapshot de l'état actuel pour détecter les changements."""
        return tuple((obj.x, obj.y, type(obj).__name__) for obj in self.model.list_objects)
    
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
    
    def __del__(self):
        """Nettoyer proprement curses à la destruction de la vue."""
        try:
            curses.curs_set(1)  # Réafficher le curseur
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()
        except:
            pass