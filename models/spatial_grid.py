import math
from typing import List, Tuple

class SpatialGrid:
    """
    Grille spatiale pour optimiser la recherche de voisins.
    Gère les objets (unités/obstacles).
    """
    
    def __init__(self, width: float, height: float, cell_size: float = 10.0):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = int(math.ceil(width / cell_size))
        self.rows = int(math.ceil(height / cell_size))
        self.grid = {}
    
    def clear(self):
        """Vide toute la grille"""
        self.grid.clear()
    
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Retourne l'index de cellule pour une position"""
        col = max(0, min(self.cols - 1, int(x / self.cell_size)))
        row = max(0, min(self.rows - 1, int(y / self.cell_size)))
        return (col, row)
    
    def add_object(self, obj):
        """Ajoute un objet (unité ou obstacle) à la grille"""
        cell = self._get_cell(obj.x, obj.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(obj)
    
    def get_nearby_objects(self, x: float, y: float) -> List:
        """Retourne tous les objets dans les 9 cellules voisines"""
        nearby = []
        cell = self._get_cell(x, y)
        
        for dc in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                check_cell = (cell[0] + dc, cell[1] + dr)
                if check_cell in self.grid:
                    nearby.extend(self.grid[check_cell])
        
        return nearby


