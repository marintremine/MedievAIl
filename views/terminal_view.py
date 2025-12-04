import curses
import sys
import io

from time import time
from views.battle_view import BattleView
from models.battle_model import BattleModel
from models.unit import *

# Modes de vues
VIEW_BATTLE = 0
VIEW_ARMY_INFO = 1
VIEW_MESSAGE = 2

class TerminalView(BattleView):
    def __init__(self, model, controller):
        super().__init__(model, controller)
        self._init_curses()
        self._init_colors()

        self.view_mode = VIEW_BATTLE

        self.view_offsets = {
            VIEW_BATTLE: [0, 0],
            VIEW_ARMY_INFO: [0, 0],
            VIEW_MESSAGE: [0, 0]
        }

        self._stdout_buffer = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = self._stdout_buffer


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
    
    def render(self):
        """Rendu principal de la vue terminal."""
        self.stdscr.erase()

        if self.view_mode == VIEW_BATTLE:
            self._draw_map()
            self._draw_units()
            self._draw_info()
        elif self.view_mode == VIEW_ARMY_INFO:
            self._draw_army_infos()
        elif self.view_mode == VIEW_MESSAGE:
            text = self._stdout_buffer.getvalue()
            self._draw_standard_output(text, 0)

        self.stdscr.refresh()
    
    def _draw_map(self):
        """Dessine la carte de base (terrain)."""
        max_y, max_x = self.stdscr.getmaxyx()
        for y in range(min(self.model.map_height, max_y)):
            for x in range(min(self.model.map_width, max_x)):

                offset_x, offset_y = self.view_offsets[self.view_mode]
                map_x = x + offset_x
                map_y = y + offset_y
                
                if map_y >= self.model.map_height or map_x >= self.model.map_width:
                    continue
                try:
                    self.stdscr.addch(y, x, '.', curses.color_pair(3))
                except curses.error:
                    pass

    def _draw_units(self):
        """Dessine les unités sur la carte."""
        max_y, max_x = self.stdscr.getmaxyx()
        for obj in self.model.list_objects:
            if isinstance(obj, Unit) and not obj.is_alive():
                continue

            offset_x, offset_y = self.view_offsets[self.view_mode]
            screen_x = obj.x - offset_x
            screen_y = obj.y - offset_y

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

    def _draw_army_infos(self):
        """Affiche les informations des armées côte à côte avec scroll vertical."""
        max_y, max_x = self.stdscr.getmaxyx()
        start_x = 0

        half_width = max(1, max_x // 2)

        armies = [
            (self.model.get_army(self.model.general_1), self.model.general_1, "Armée 1"),
            (self.model.get_army(self.model.general_2), self.model.general_2, "Armée 2")
        ]

        # Récupérer l'offset Y spécifique à la vue ARMEE_INFO
        offset_y = self.view_offsets.get(VIEW_ARMY_INFO, [0, 0])[1]

        for army, general, army_name in armies:
            # Construire les lignes de l'armée (header + unités)
            taille_armee = len(army)
            header = f"{army_name} (Général: {general.name} - Taille de l'armée: {taille_armee})"
            lines = [header] + [
                f"- {unit.name} | HP: {unit.hp}/{unit.max_hp} | Pos: ({unit.x},{unit.y})"
                for unit in army
            ]

            # Afficher uniquement les lignes visibles en tenant compte de offset_y
            for idx, line in enumerate(lines):
                screen_y = idx - offset_y
                if 0 <= screen_y < max_y:
                    try:
                        if idx == 0:
                            # header en couleur du général
                            color = curses.color_pair(self.general_colors.get(general, 3)) | curses.A_BOLD
                            self.stdscr.addstr(screen_y, start_x, line[:half_width - 1], color)
                        else:
                            self.stdscr.addstr(screen_y, start_x, line[:half_width - 1])
                    except curses.error:
                        pass

            start_x += half_width  # Déplacer à droite pour la prochaine armée

    def _draw_standard_output(self, text, start_y):
        """Affiche du texte standard à l'écran."""
        max_y, max_x = self.stdscr.getmaxyx()
        lines = text.splitlines()
        for i, line in enumerate(lines):
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
            sys.stdout = self._original_stdout
            curses.curs_set(1)       # réaffiche le curseur
            curses.nocbreak()        # désactive le mode cbreak
            self.stdscr.keypad(False)
            curses.echo()            # réactive l'écho des touches
            curses.endwin()          # ferme curses proprement
        except:
            pass

    def next_view_mode(self):
        """Change le mode de vue."""
        self.view_mode = (self.view_mode + 1) % 3

    def prev_view_mode(self):
        """Change le mode de vue."""
        self.view_mode = (self.view_mode - 1) % 3

    def move_view(self, dx, dy):
        """Déplace la caméra sur la carte pour la vue active."""
        offset = self.view_offsets[self.view_mode]
        offset[0] = max(0, min(offset[0] + dx, self.model.map_width - 1))
        offset[1] = max(0, min(offset[1] + dy, self.model.map_height - 1))

    def move_view_fast(self, dx, dy):
        """Déplace rapidement la caméra sur la carte pour la vue active."""
        offset = self.view_offsets[self.view_mode]
        offset[0] = max(0, min(offset[0] + dx * 5, self.model.map_width - 1))
        offset[1] = max(0, min(offset[1] + dy * 5, self.model.map_height - 1))

    def scroll_up(self):
        """Scroll pour la vue active."""
        offset = self.view_offsets[self.view_mode]
        offset[1] = max(0, offset[1] - 1)

    def scroll_down(self):
        """Scroll pour la vue active."""
        offset = self.view_offsets[self.view_mode]
        offset[1] = min(self.model.map_height - 1, offset[1] + 1)