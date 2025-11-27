import curses
import sys
import termios

from time import time
from views.battle_view import BattleView
from models.battle_model import BattleModel
from models.unit import *

class TerminalView(BattleView):
    def __init__(self, model, controller):
        super().__init__(model, controller)
        self._init_curses()
        self._init_colors()
        self.offset_x = 0
        self.offset_y = 0

    def _init_curses(self):
        """Initialise les paramètres de curses."""
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)  # Masquer le curseur
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)  # Non-bloquant pour les inputs

    def _init_colors(self):
        """Initialise les paires de couleurs pour l'affichage."""
        curses.start_color()
        curses.use_default_colors()
        
        # Définir les paires de couleurs
        curses.init_pair(1, curses.COLOR_RED, -1)  # Général 1
        curses.init_pair(2, curses.COLOR_BLUE, -1)  # Général 2
        curses.init_pair(3, curses.COLOR_WHITE, -1)  # Terrain
        
        # Mapper les généraux aux couleurs
        self.general_colors = {
            self.model.general_1: 1,
            self.model.general_2: 2
        }
    
    def render(self) -> None:
        """Affiche l'ensemble de la vue en mode terminal."""
        self.stdscr.erase()
        self._draw_map()
        self._draw_units()
        self._draw_info()

        # Afficher les infos de l'unité sélectionnée
        distance_threshold = 5
        for unit in self.model.list_objects:
            self._draw_unit_info(unit, start_y=self.model.map_height + distance_threshold)
            distance_threshold += 6
        self.stdscr.refresh()

        
        # Rafraîchir l'écran une seule fois à la fin
        self.stdscr.refresh()
    
    def _draw_map(self):
        """Dessine la carte de base (terrain)."""
        max_y, max_x = self.stdscr.getmaxyx()
        for y in range(min(self.model.map_height, max_y)):
            for x in range(min(self.model.map_width, max_x)):
                map_x = x + self.offset_x
                map_y = y + self.offset_y
                if map_y >= self.model.map_height or map_x >= self.model.map_width:
                    continue
                try:
                    self.stdscr.addch(y, x, '.', curses.color_pair(3))
                except curses.error:
                    pass

    def _draw_units(self):
        max_y, max_x = self.stdscr.getmaxyx()
        for obj in self.model.list_objects:
            if isinstance(obj, Unit) and not obj.is_alive():
                continue

            screen_x = obj.x - self.offset_x
            screen_y = obj.y - self.offset_y

            if 0 <= screen_y < max_y and 0 <= screen_x < max_x:
                symbol = self._get_unit_symbol(obj)
                color_pair = self._get_unit_color(obj)
                try:
                    self.stdscr.addch(screen_y, screen_x, symbol,
                                    curses.color_pair(color_pair) | curses.A_BOLD)
                except curses.error:
                    pass


    def _draw_info(self):
        """Affiche les informations de statut en bas de l'écran."""
        max_y, max_x = self.stdscr.getmaxyx()
        status_y = min(self.model.map_height + 1, max_y - 1)
        time_str = f"Temps : {time():.1f}s"
        running_str = "RUNNING" if self.model.running else "PAUSED"
        speed_str = f"Speed: {self.controller.game_speed}x"
        info_line = f"{time_str}   |   État : {running_str}   |   {speed_str}"
        try:
            self.stdscr.addstr(status_y, 0, info_line[:max_x - 1])
        except curses.error:
            pass

    def _draw_unit_info(self, unit, start_y):
        """Affiche les informations détaillées d'une unité spécifique."""
        max_y, max_x = self.stdscr.getmaxyx()
        info_lines = [
            f"Unité: {unit.name}",
            f"HP: {unit.hp}/{unit.max_hp}",
            f"Position: ({unit.x}, {unit.y})",
            f"Action: {unit.currentAction}",
            f"Cooldown: {unit.cooldown_timer}/{unit.cooldown}"
        ]
        for i, line in enumerate(info_lines):
            y = start_y + i
            if y < max_y:
                try:
                    self.stdscr.addstr(y, 0, line[:max_x - 1])
                except curses.error:
                    pass

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
        """Restaure les paramètres du terminal pour éviter les codes d'échappement."""
        try:
            curses.curs_set(1)       # réaffiche le curseur
            curses.nocbreak()        # désactive le mode cbreak
            self.stdscr.keypad(False)
            curses.echo()            # réactive l'écho des touches
            curses.endwin()          # ferme curses proprement
        except:
            pass

    def move_view(self, dx, dy):
        """Déplace la caméra sur la carte."""
        self.offset_x = max(0, min(self.offset_x + dx, self.model.map_width - 1))
        self.offset_y = max(0, min(self.offset_y + dy, self.model.map_height - 1))