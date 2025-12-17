from __future__ import annotations
import math
from models.order import *
import random
from models.object import Object

class Unit(Object):
    def __init__(self, name: str, general, hp: int, attack: int, armor: int, pierce_armor: int,
                 range_: int, line_of_sight: int, speed: float, attack_delay: float, reload_time: float, 
                 x: int, y: int, density: float, radius: float, bonus_attacks: dict, battle_model):
        # Appel au constructeur parent avec radius et density
        super().__init__(x, y, radius, density, battle_model)
        
        self.name = name
        self.general = general
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.armor = armor
        self.pierce_armor = pierce_armor
        self.range = range_
        self.line_of_sight = line_of_sight
        self.speed = speed
        self.attack_delay = attack_delay
        self.reload_time = reload_time

        self.current_attack_delay = 0 
        self.current_reload_time = 0

        self.order = Wait(self) 
        self.currentAction = "stand"
        self.direction = (0, 1)
        self.bonus_attacks = bonus_attacks
        self.vx = 0.0
        self.vy = 0.0

    def is_alive(self) -> bool:
        """Vérifie si l'unité est encore en vie"""
        return self.hp > 0
    
    def in_range(self, target: "Unit") -> bool:
        """Vérifie si la cible est à portée d'attaque"""
        dist = math.hypot(self.x - target.x, self.y - target.y)
        return dist <= self.range + self.radius
    
    def in_sight(self, target: "Unit") -> bool:
        """Vérifie si la cible est dans le champ de vision"""
        dist = math.hypot(self.x - target.x, self.y - target.y)
        return dist <= self.line_of_sight + self.radius
    
    def enemies_in_sight(self):
        """Retourne une liste des unités ennemies dans le champ de vision dans le champ de vision du plus proche au plus éloigné"""
        enemies = [
            enemy for enemy in self.battle_model.get_enemy_army(self.general)
            if self.in_sight(enemy) and enemy.is_alive()
        ]
        enemies.sort(key=lambda u: math.hypot(self.x - u.x, self.y - u.y))
        return enemies

    def enemies_in_range(self):
        """Retourne une liste des unités ennemies à portée d'attaque du plus proche au plus éloigné"""
        enemies = [
            enemy for enemy in self.battle_model.get_enemy_army(self.general)
            if self.in_range(enemy) and enemy.is_alive()
        ]
        enemies.sort(key=lambda u: math.hypot(self.x - u.x, self.y - u.y))
        return enemies
    
    def nearest_enemies(self):
        """Retourne une listes des unités ennemies du plus proche au plus éloigné"""
        enemies = [
            enemy for enemy in self.battle_model.get_enemy_army(self.general)
            if enemy.is_alive()
        ]
        enemies.sort(key=lambda u: math.hypot(self.x - u.x, self.y - u.y))
        return enemies

    def action(self) -> None:
        """Exécute l'action actuelle de l'unité"""
        if not self.is_alive():
            return
        
        # Décrémenter le temps de rechargement qu'importe l'action
        if self.current_reload_time > 0:
            self.current_reload_time -= 1 * self.battle_model.delta_time
        self.order.action()

    def _apply_damage(self, target: "Unit"):
        """Calcul des dégâts séparé pour être réutilisable"""
        damage = self.attack - target.armor
        pierce_damage = self.attack - target.pierce_armor
        bonus = self.bonus_attacks.get(type(target), 0)
        total_damage = max(damage, pierce_damage, 0) + bonus
        target.hp -= total_damage

    def attack_target(self, target: "Unit") -> bool:
        """Effectue une attaque sur la cible spécifiée"""
        if not self.is_alive() or not target.is_alive() or not self.in_range(target):
            self.current_attack_delay = 0 # Reset si attaque impossible
            return False
        
        # Si on est encore en train de recharger l'arme (Cooldown), on ne fait rien
        if self.current_reload_time > 0:
            self.currentAction = "stand" # On attend
            return False

        self.currentAction = "attack"
        # Si l'animation d'attaque n'est pas finie (Wind-up)
        if self.current_attack_delay < self.attack_delay:
                self.current_attack_delay += self.battle_model.delta_time
                return False # L'attaque n'est pas encore partie
        
        # --- L'ATTAQUE PART ICI ---
        self._apply_damage(target)
        
        # Réinitialiser le délai d'attaque et le cooldown
        self.current_attack_delay = 0
        self.current_reload_time = self.reload_time

        return True
    
    def move_towards(self, tx: float, ty: float) -> bool:
        """
        Déplacement unifié avec flocking : gère collision avec unités ET obstacles.
        """
        if not self.is_alive():
            return
        
        # === 1. DIRECTION VERS LA CIBLE ===
        dx = tx - self.x
        dy = ty - self.y
        distance = math.hypot(dx, dy)
        
        if distance < self.radius * 2:
            self.vx = 0.0
            self.vy = 0.0
            self.currentAction = "stand"
            return True  # Arrivé à destination
        
        # Direction normalisée
        target_vx = (dx / distance) * self.speed
        target_vy = (dy / distance) * self.speed
        
        # === 2. SÉPARATION UNIFIÉE (unités + obstacles) ===
        separation_vx = 0.0
        separation_vy = 0.0
        separation_radius = self.radius * 6
        
        # Récupérer TOUS les objets proches (unités + obstacles)
        nearby_objects = self.battle_model.spatial_grid.get_nearby_objects(self.x, self.y)
        
        for other in nearby_objects:
            if other is self or not other.is_alive():
                continue
            
            # Distance à l'autre objet
            dx_sep = self.x - other.x
            dy_sep = self.y - other.y
            dist = math.hypot(dx_sep, dy_sep)
            
            if dist < separation_radius and dist > 0.001:
                # Force proportionnelle à la proximité
                force = (separation_radius - dist) / separation_radius
                
                # Pondérer par la densité
                if math.isinf(other.density):
                    # Obstacle : force maximale
                    force *= 10.0
                else:
                    # Unité normale
                    force *= other.density
                
                separation_vx += (dx_sep / dist) * force * self.speed
                separation_vy += (dy_sep / dist) * force * self.speed
        
        # === 3. COMBINER LES FORCES ===
        self.vx = target_vx * 0.7 + separation_vx * 0.3
        self.vy = target_vy * 0.7 + separation_vy * 0.3
        
        # Limiter vitesse max
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed > self.speed:
            self.vx = (self.vx / current_speed) * self.speed
            self.vy = (self.vy / current_speed) * self.speed
        
        # === 4. APPLIQUER LE DÉPLACEMENT ===
        dt = self.battle_model.delta_time
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        
        # === 5. CONTRAINDRE À LA CARTE ===
        new_x = max(self.radius, min(self.battle_model.map_width - self.radius, new_x))
        new_y = max(self.radius, min(self.battle_model.map_height - self.radius, new_y))
        
        # === 6. METTRE À JOUR LA POSITION ===
        self.x = new_x
        self.y = new_y
        
        # === 7. METTRE À JOUR L'ÉTAT ===
        if abs(self.vx) > 0.01 or abs(self.vy) > 0.01:
            self.currentAction = "move"
            if self.vx != 0 or self.vy != 0:
                self.direction = (self.vx, self.vy)
        else:
            self.currentAction = "stand"

        return False  # Pas encore arrivé


    def __str__(self) -> str:
        return f"Unit({self.name}, HP: {self.hp}/{self.max_hp}, Pos: ({self.x}, {self.y}))"
    
    def to_dict(self):
        return {
            "type": self.name.lower(),
            "x": self.x,
            "y": self.y,
            "hp": self.hp,
            "current_attack_delay": self.current_attack_delay,
            "current_reload_time": self.current_reload_time
        }
    
# ============================================================================
# TYPES D'UNITÉS
# ============================================================================


class Pikeman(Unit):
    def __init__(self, general: "General", x: int, y: int, battle_model): # pyright: ignore[reportUndefinedVariable]
        super().__init__(
            name="Pikeman",
            general=general,
            hp=55,
            attack=4,
            armor=0,
            pierce_armor=0,
            range_=0,
            line_of_sight=4,
            speed=1,
            attack_delay=0.5,   
            reload_time=3.0,
            x=x,
            y=y,
            bonus_attacks={Knight: 22},
            density=1.0,
            radius=0.20,
            battle_model=battle_model,
        )


class Knight(Unit):
    def __init__(self, general: "General", x:int, y:int, battle_model): # pyright: ignore[reportUndefinedVariable]
        super().__init__(
            name="Knight",
            general=general,
            hp=100,
            attack=10,
            armor=2,
            pierce_armor=2,
            range_=0,
            line_of_sight=4,
            speed=1.35,
            attack_delay=0.35,
            reload_time=1.8,
            x=x,
            y=y,
            bonus_attacks={},
            density=3.0,
            radius=0.35,
            battle_model=battle_model
        )


class Crossbowman(Unit):
    def __init__(self, general: "General", x:int, y:int, battle_model): # pyright: ignore[reportUndefinedVariable]
        super().__init__(
            name="Crossbowman",
            general=general,
            hp=35,
            attack=5,
            armor=0,
            pierce_armor=0,
            range_=5,
            line_of_sight=7,
            speed=0.96,
            attack_delay=0.35,   
            reload_time=2.0,
            x=x,
            y=y,
            bonus_attacks={},        
            density=0.8,
            radius=0.20,    
            battle_model=battle_model
        )
        self.accuracy = 0.85

    def _apply_damage(self, target: "Unit"):
        if random.random() <= self.accuracy:
            super()._apply_damage(target)
            

class Longswordsman(Unit):
    def __init__(self, general, x: int, y: int, battle_model):
        super().__init__(
            name="Longswordsman",
            general=general,
            hp=60,
            attack=9,
            armor=1,
            pierce_armor=1,
            range_= 0,
            line_of_sight=6,
            speed=0.96,
            attack_delay=0,
            reload_time=2.0,
            x= x,
            y= y,
            bonus_attacks={},
            density=1.0,
            radius=0.20,
            battle_model= battle_model,
        )



def unitFactory(unit_type, general, x, y, battle_model) -> Unit: # pyright: ignore[reportUndefinedVariable]
    unit_classes = {
        "pikeman": Pikeman,
        "knight": Knight,
        "crossbowman": Crossbowman,
        "longsword": Longswordsman
    }
    key = unit_type.lower()
    if key in unit_classes:
        return unit_classes[key](general, x, y, battle_model)
    else:
        raise ValueError(f"Unknown unit type: {key}")
    
