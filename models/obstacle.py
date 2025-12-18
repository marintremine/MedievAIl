from models.unit import Object
import math

class Obstacle(Object):
    """
    Obstacle avec système unifié de collision.
    
    REPRÉSENTATION TERMINAL :
    - x, y = coin supérieur gauche
    - sizeX, sizeY = dimensions en cases
    - radius = rayon pour collision circulaire (calculé depuis dimensions)
    - cx, cy = centre pour calculs de distance
    
    Exemple pour affichage :
    Rock 10x10 à position (5, 5) occupe les cases de (5,5) à (15,15)
    """
    
    def __init__(self, x: int, y: int, sizeX: int, sizeY: int, battle_model, type_="Obstacle"):
        # Calculer le rayon effectif (demi-diagonale du rectangle)
        radius = math.hypot(sizeX, sizeY) / 2.0
        
        # Densité infinie = immuable (ne bouge jamais)
        density = float('inf')
        
        # Centre du rectangle (pour calculs de distance)
        cx = x + sizeX / 2.0
        cy = y + sizeY / 2.0
        
        # Appeler le constructeur parent avec le centre
        super().__init__(cx, cy, radius, density, battle_model)
        
        # Propriétés spécifiques aux obstacles
        self.type = type_
        self.sizeX = sizeX
        self.sizeY = sizeY
        
        # Stocker aussi le coin supérieur gauche (pour affichage)
        self.corner_x = x
        self.corner_y = y
        
        # Centre (déjà dans self.x, self.y mais on garde des alias explicites)
        self.cx = self.x
        self.cy = self.y
    
    def __str__(self):
        return f"Obstacle({self.type}) at ({self.corner_x}, {self.corner_y}) size={self.sizeX}x{self.sizeY}"
    
    def to_dict(self):
        return {
            "type": self.type,
            "x": self.corner_x,  # Sauvegarder le coin, pas le centre
            "y": self.corner_y,
            "sizeX": self.sizeX,
            "sizeY": self.sizeY,
        }
    
    def get_occupied_cells(self):
        """
        Retourne la liste des cellules (x, y) occupées par l'obstacle.
        Utile pour l'affichage terminal.
        
        Exemple : Rock 3x3 à (5, 5) retourne [(5,5), (5,6), (5,7), (6,5), ...]
        """
        cells = []
        for dx in range(self.sizeX):
            for dy in range(self.sizeY):
                cells.append((self.corner_x + dx, self.corner_y + dy))
        return cells
    
    def contains_point(self, x: float, y: float) -> bool:
        """Vérifie si un point est à l'intérieur de l'obstacle (collision rectangulaire)"""
        return (self.corner_x <= x < self.corner_x + self.sizeX and 
                self.corner_y <= y < self.corner_y + self.sizeY)


# ============================================================================
# TYPES D'OBSTACLES
# ============================================================================

class Bush(Obstacle):
    def __init__(self, x: int, y: int, battle_model):
        super().__init__(
            x=x,
            y=y,
            sizeX=5,
            sizeY=5,
            battle_model=battle_model,
            type_="Bush"
        )


class Rock(Obstacle):
    def __init__(self, x: int, y: int, battle_model):
        super().__init__(
            x=x,
            y=y,
            sizeX=10,
            sizeY=10,
            battle_model=battle_model,
            type_="Rock"
        )


class Tree(Obstacle):
    def __init__(self, x: int, y: int, battle_model):
        super().__init__(
            x=x,
            y=y,
            sizeX=3,
            sizeY=3,
            battle_model=battle_model,
            type_="Tree"
        )


def ObstacleFactory(obs_type: str, x: int, y: int, battle_model) -> Obstacle:
    obstacle_classes = {
        "bush": Bush,
        "rock": Rock,
        "tree": Tree,
    }
    key = obs_type.lower()
    if key in obstacle_classes:
        return obstacle_classes[key](x, y, battle_model)
    else:
        raise ValueError(f"Unknown obstacle type: {key}")



def ObstacleFactory(obs_type: str, x: int, y: int, battle_model) -> Obstacle:
    obstacle_classes = {
        "bush": Bush,
        "rock": Rock,
        "tree": Tree,
    }
    key = obs_type.lower()
    if key in obstacle_classes:
        return obstacle_classes[key](x, y, battle_model)
    else:
        raise ValueError(f"Unknown obstacle type: {key}")

