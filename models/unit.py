from __future__ import annotations
from models import battle_model
from models.order import Wait, Attack, Move
import random

class Object:
    def __init__(self, x: int, y: int, battle_model) -> None:
        self.x = x
        self.y = y
        self.battle_model = battle_model

class Unit(Object):
    def __init__(self, name: str, general: "General", hp: int, attack: int, armor: int, pierce_armor: int, # pyright: ignore[reportUndefinedVariable]
                 range_: int, line_of_sight: int, speed: float, attack_delay: float, reload_time: float, x: int, y: int, bonus_attacks: dict, battle_model, occupancy):
        super().__init__(x, y, battle_model)
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
        self.attack_delay = attack_delay # Temps d'animation (Bloquant)
        self.reload_time = reload_time # Temps de recharge (Non-bloquant)

        self.current_attack_delay = 0 
        self.current_reload_time = 0
        self.move_progress = 0

        self.order = Wait(self)
        self.currentAction = "stand"
        self.direction = (0, 1)
        self.bonus_attacks = bonus_attacks
        self.occupancy = occupancy

    def is_alive(self) -> bool:
        """Vérifie si l'unité est encore en vie"""
        return self.hp > 0
    
    def in_range(self, target: "Unit") -> bool:
        """Vérifie si la cible est à portée d'attaque"""
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        return distance <= self.range
    
    def in_sight(self, target: "Unit") -> bool:
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        return distance <= self.line_of_sight
    
    def enemies_in_sight(self):
        """Retourne une liste des unités ennemies dans le champ de vision dans le champ de vision du plus proche au plus éloigné"""
        enemies = [
            enemy for enemy in self.battle_model.get_enemy_army(self.general)
            if self.in_sight(enemy) and enemy.is_alive()
        ]
        enemies.sort(key=lambda u: abs(self.x - u.x) + abs(self.y - u.y))
        return enemies

    def enemies_in_range(self):
        """Retourne une liste des unités ennemies à portée d'attaque du plus proche au plus éloigné"""
        enemies = [
            enemy for enemy in self.battle_model.get_enemy_army(self.general)
            if self.in_range(enemy) and enemy.is_alive()
        ]
        enemies.sort(key=lambda u: abs(self.x - u.x) + abs(self.y - u.y))
        return enemies
    
    def nearest_enemies(self):
        """Retourne une listes des unités ennemies du plus proche au plus éloigné"""
        enemies = [
            enemy for enemy in self.battle_model.get_enemy_army(self.general)
            if enemy.is_alive()
        ]
        enemies.sort(key=lambda u: abs(self.x - u.x) + abs(self.y - u.y))
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

    def move(self, new_x: int, new_y: int) -> bool:
        """Déplace l'unité vers les coordonnées spécifiées"""
        #if not self.is_alive() or not self.battle_model.is_in_map(new_x, new_y) or self.battle_model.is_obstacle_at(new_x, new_y):
        if not self.is_alive() or not self.battle_model.is_coord_accessible(new_x, new_y, self):
            return False
        
        self.current_attack_delay = 0.0 # Reset attaque si déplacement

        self.currentAction = "walk"
        # Calcul direction
        dx = new_x - self.x
        dy = new_y - self.y

        dx = (dx > 0) - (dx < 0)
        dy = (dy > 0) - (dy < 0)

        self.direction = (dx, dy)
    
        # Mouvement progressif
        self.move_progress += self.speed * self.battle_model.delta_time
        
        if self.move_progress >= 1.0:
            self.battle_model.objects['state_map'][(self.x, self.y)].discard(self)
            self.x = new_x
            self.y = new_y
            self.move_progress -= 1.0
            self.battle_model.objects['state_map'][(new_x, new_y)].add(self)
            return True
        
        return False

    def __str__(self) -> str:
        return f"Unit({self.name}, HP: {self.hp}/{self.max_hp}, Pos: ({self.x}, {self.y}))"
    
    def to_dict(self):
        return {
            "type": self.name.lower(),
            "x": self.x,
            "y": self.y,
            "hp": self.hp,
            "current_attack_delay": self.current_attack_delay,
            "current_reload_time": self.current_reload_time,
            "move_progress": self.move_progress
        }


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
            battle_model= battle_model,
            occupancy=0.20
        )


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
            battle_model=battle_model,
            occupancy = 0.40
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
            battle_model=battle_model,
            occupancy=1
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
            battle_model=battle_model,
            occupancy=0.40
        )
        self.accuracy = 0.85

    def _apply_damage(self, target: "Unit"):
        if random.random() <= self.accuracy:
            super()._apply_damage(target)


def unitFactory(unit_type, general, x, y, battle_model) -> Unit: # pyright: ignore[reportUndefinedVariable]
    unit_classes = {
        "pikeman": Pikeman,
        "knight": Knight,
        "crossbowman": Crossbowman,
        "longswordsman": Longswordsman
    }
    key = unit_type.lower()
    if key in unit_classes:
        return unit_classes[key](general, x, y, battle_model)
    else:
        raise ValueError(f"Unknown unit type: {key}")