import math


class Object:
    """
    Classe de base pour tous les objets du jeu (unités, obstacles, etc.)
    Maintenant avec radius et density pour unifier le système de collision.
    """
    def __init__(self, x: float, y: float, radius: float, density: float, battle_model) -> None:
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.density = density
        self.battle_model = battle_model
    
    def is_alive(self) -> bool:
        """Par défaut, tous les objets sont "vivants" (peuvent interagir)"""
        return True
    def distance_to(self, other: "Object") -> float:
        """Calcule la distance euclidienne entre cet objet et un autre"""
        return math.hypot(self.x - other.x, self.y - other.y)
    def to_dict(self) -> dict:
        """Sérialisation de l'objet en dictionnaire"""
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "density": self.density,
        }