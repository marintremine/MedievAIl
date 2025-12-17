import curses
import sys
import io

from time import time
from views.battle_view import BattleView
from models.unit import *
from models.obstacle import *

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
        
        if self.model.general_1 not in self.general_colors \
        or self.model.general_2 not in self.general_colors:
            self._init_colors()

        if self.view_mode == VIEW_BATTLE:
            self._draw_header()
            self._draw_map()
            self._draw_units()
            self._draw_obstacles()
            self._draw_info()
        elif self.view_mode == VIEW_ARMY_INFO:
            self._draw_army_infos()
        elif self.view_mode == VIEW_MESSAGE:
            text = self._stdout_buffer.getvalue()
            self._draw_standard_output(text, 0)

        self.stdscr.refresh()

    def _draw_header(self):
        """Affiche les infos des généraux sur la première ligne (fixe)."""
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Récupération des données
        g1 = self.model.general_1
        g2 = self.model.general_2
        army1_size = len(self.model.get_army(g1))
        army2_size = len(self.model.get_army(g2))
        
        # Construction des chaînes
        empty_line = " " * (max_x - 1)
        self.stdscr.addstr(0, 0, empty_line)

        # Affichage Général 1 (Gauche)
        info_g1 = f"{g1.name} : {army1_size} unités"
        color_g1 = self.general_colors.get(g1, 1) | curses.A_BOLD # Couleur du général 1 en gras
        self.stdscr.addstr(0, 0, info_g1, curses.color_pair(color_g1))

        # Affichage Général 2 (Droite)
        info_g2 = f"{g2.name} : {army2_size} unités"
        color_g2 = self.general_colors.get(g2, 3) | curses.A_BOLD
        
        # Calcul pour aligner à droite
        pos_x_g2 = max(0, max_x - len(info_g2) - 1)

        if pos_x_g2 > len(info_g1) + 2:
             self.stdscr.addstr(0, pos_x_g2, info_g2, curses.color_pair(color_g2))

    def _draw_map(self):
        """Dessine la carte entre le Header et le Footer."""
        max_y, max_x = self.stdscr.getmaxyx()
        
        top_margin = 1      # Header
        bottom_margin = 3   # Footer
        
        # La hauteur disponible pour la carte
        visual_limit_y = max_y - bottom_margin

        for y in range(self.model.map_height):
            # Si on dépasse logiquement la zone visible, on arrête la boucle Y
            if y + top_margin >= visual_limit_y: 
               break

            for x in range(min(self.model.map_width, max_x)):
                offset_x, offset_y = self.view_offsets[self.view_mode]
                
                # Coordonnées carte
                map_x = x + offset_x
                map_y = y + offset_y
                
                # Position écran
                screen_y = y + top_margin
                
                # Si on tape dans le footer, on n'affiche pas
                if screen_y >= visual_limit_y:
                    continue

                if map_y >= self.model.map_height or map_x >= self.model.map_width:
                    continue
                
                try:
                    self.stdscr.addch(screen_y, x, '.', curses.color_pair(3))
                except curses.error:
                    pass

    def _draw_units(self):
        """Dessine les unités en respectant Header et Footer."""
        max_y, max_x = self.stdscr.getmaxyx()
        top_margin = 1
        bottom_margin = 3
        
        visual_limit_y = max_y - bottom_margin

        for obj in self.model.get_units():
            if isinstance(obj, Unit) and not obj.is_alive():
                continue

            offset_x, offset_y = self.view_offsets[self.view_mode]
            
            screen_x = obj.x - offset_x
            screen_y = (obj.y - offset_y) + top_margin 

            # Vérification entre header et footer
            if top_margin <= screen_y < visual_limit_y and 0 <= screen_x < max_x:
                symbol = self._get_object_symbol(obj)
                color_pair = self._get_unit_color(obj)
                try:
                    self.stdscr.addch(screen_y, screen_x, symbol,
                                    curses.color_pair(color_pair) | curses.A_BOLD)
                except curses.error:
                    pass

    def _draw_obstacles(self):
        """Clipping complet : Header (Haut) et Footer (Bas)."""
        max_y, max_x = self.stdscr.getmaxyx()
        map_width = self.model.map_width
        map_height = self.model.map_height
        
        top_margin = 1
        bottom_margin = 3
        
        # La ligne à ne pas dépasser vers le bas
        visual_limit_y = max_y - bottom_margin

        offset_x, offset_y = self.view_offsets[self.view_mode]

        for obj in self.model.get_obstacles():
            delta_x = obj.sizeX // 2
            delta_y = obj.sizeY // 2

            world_x = obj.x - delta_x
            world_y = obj.y - delta_y

            screen_x = world_x - offset_x
            screen_y = (world_y - offset_y) + top_margin
            
            # --- Clipping VERTICAL (Y) ---
            # On coupe si ça rentre dans le Header
            start_dy_screen = max(0, top_margin - screen_y)
            
            # On coupe si ça sort de la carte (en haut)
            start_dy_map = max(0, -world_y)
            start_dy = max(start_dy_screen, start_dy_map)

            # Calcul de la limite entre le bas de l'objet et le Footer / bas de la Map
            space_before_footer = visual_limit_y - screen_y
            space_before_map_end = map_height - world_y

            # On coupe si ça rentre dans le Footer ou sort de la carte (en bas)
            end_dy = min(obj.sizeY, space_before_footer, space_before_map_end)

            # --- Clipping HORIZONTAL (X) --- (Standard)
            start_dx_screen = max(0, -screen_x)
            start_dx_map = max(0, -world_x)
            start_dx = max(start_dx_screen, start_dx_map)

            limit_screen_x = max_x - screen_x
            limit_map_x = map_width - world_x
            end_dx = min(obj.sizeX, limit_screen_x, limit_map_x)

            if start_dy < end_dy and start_dx < end_dx:
                symbol = self._get_object_symbol(obj)
                color = curses.color_pair(3)
                try:
                    for dy in range(start_dy, end_dy):
                        for dx in range(start_dx, end_dx):
                            self.stdscr.addch(
                                screen_y + dy,
                                screen_x + dx,
                                symbol,
                                color
                            )
                except curses.error:
                    pass

    def _draw_info(self):
        """Affiche le footer fixe (3 dernières lignes)."""
        max_y, max_x = self.stdscr.getmaxyx()
        
        # On définit les lignes fixes en partant du bas
        line_info = max_y - 1
        line_keys2 = max_y - 2
        line_keys1 = max_y - 3

        # Si l'écran est trop petit pour afficher les infos, on n'affiche rien
        if max_y < 4:
            return

        touches = "[F1] Vue précédente | [F2] Vue suivante | [F3] Sauvegarder | [F4] Charger"
        touches2 = "[Flèches]/[ZQSD] Déplacer vue | [P] Pause/Reprendre | [+/-] Vitesse | [ECHAP] Quitter"
        time_str = f"Temps : {time():.1f}s"
        running_str = "RUNNING" if self.model.running else "PAUSED"
        speed_str = f"Speed: {self.controller.game_speed}x"
        info_line = f"{time_str}   |   État : {running_str}   |   {speed_str}"
        
        try:
            # On nettoie la zone du footer pour éviter les traînées de la carte
            empty = " " * (max_x - 1)
            self.stdscr.addstr(line_keys1, 0, empty, curses.A_REVERSE)
            self.stdscr.addstr(line_keys2, 0, empty, curses.A_REVERSE)
            self.stdscr.addstr(line_info, 0, empty, curses.A_REVERSE)

            # On écrit le texte
            self.stdscr.addstr(line_keys1, 0, touches[:max_x - 1], curses.A_REVERSE)
            self.stdscr.addstr(line_keys2, 0, touches2[:max_x - 1], curses.A_REVERSE)
            self.stdscr.addstr(line_info, 0, info_line[:max_x - 1], curses.A_REVERSE)
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

    def _get_object_symbol(self, obj):
        """Définit un symbole simple pour représenter les unités."""
        if isinstance(obj, Knight):
            return "K"
        elif isinstance(obj, Pikeman):
            return "P"
        elif isinstance(obj, Crossbowman):
            return "C"
        elif isinstance(obj, Longswordsman):
            return "L"
        elif isinstance(obj, Bush):
            return "B"
        elif isinstance(obj, Rock):
            return "R"
        elif isinstance(obj, Tree):
            return "T"
        return "U"
    
    def _get_unit_color(self, unit):
        """Retourne la couleur associée au général de l'unité."""
        if hasattr(unit, 'general') and unit.general in self.general_colors:
            return self.general_colors[unit.general]
        return 3
    
    def cleanup(self):
        """Restaure les paramètres du terminal et affiche les logs."""

        captured_logs = self._stdout_buffer.getvalue()

        try:
            curses.curs_set(1)       # réaffiche le curseur
            curses.nocbreak()        # désactive le mode cbreak
            self.stdscr.keypad(False)
            curses.echo()            # réactive l'écho des touches
            curses.endwin()          # ferme curses proprement (revient au terminal normal)
        except:
            pass
        finally:
            # Restauration de la sortie standard
            sys.stdout = self._original_stdout
            if captured_logs:
                print(captured_logs)

    def next_view_mode(self):
        """Change le mode de vue."""
        self.view_mode = (self.view_mode + 1) % 3

    def prev_view_mode(self):
        """Change le mode de vue."""
        self.view_mode = (self.view_mode - 1) % 3

    def move_view(self, dx, dy):
        """Déplace la caméra sur la carte pour la vue battle."""
        if self.view_mode != VIEW_BATTLE:
            return
        
        offset = self.view_offsets[self.view_mode]
        offset[0] = max(0, min(offset[0] + dx, self.model.map_width - 1))
        offset[1] = max(0, min(offset[1] + dy, self.model.map_height - 1))

    def move_view_up(self):
        """Déplace la caméra vers le haut pour la vue battle."""
        self.move_view(0, -1)

    def move_view_down(self):
        """Déplace la caméra vers le bas pour la vue battle."""
        self.move_view(0, 1)

    def move_view_left(self):
        """Déplace la caméra vers la gauche pour la vue battle."""
        self.move_view(-1, 0)

    def move_view_right(self):
        """Déplace la caméra vers la droite pour la vue battle."""
        self.move_view(1, 0)

    def move_view_fast(self, dx, dy):
        """Déplace rapidement la caméra sur la carte pour la vue battle."""
        if self.view_mode != VIEW_BATTLE:
            return
        
        offset = self.view_offsets[self.view_mode]
        offset[0] = max(0, min(offset[0] + dx * 5, self.model.map_width - 1))
        offset[1] = max(0, min(offset[1] + dy * 5, self.model.map_height - 1))

    def move_view_up_fast(self):
        """Déplace rapidement la caméra vers le haut pour la vue battle."""
        self.move_view_fast(0, -1)

    def move_view_down_fast(self):
        """Déplace rapidement la caméra vers le bas pour la vue battle."""
        self.move_view_fast(0, 1)

    def move_view_left_fast(self):
        """Déplace rapidement la caméra vers la gauche pour la vue battle."""
        self.move_view_fast(-1, 0)

    def move_view_right_fast(self):
        """Déplace rapidement la caméra vers la droite pour la vue battle."""
        self.move_view_fast(1, 0)

    def scroll_up(self):
        """Scroll pour la vue info armée."""
        if self.view_mode != VIEW_ARMY_INFO:
            return
        
        offset = self.view_offsets[self.view_mode]
        offset[1] = max(0, offset[1] - 1)

    def scroll_down(self):
        """Scroll pour la vue info armée."""
        if self.view_mode != VIEW_ARMY_INFO:
            return
        
        offset = self.view_offsets[self.view_mode]
        offset[1] = min(self.model.map_height - 1, offset[1] + 1)