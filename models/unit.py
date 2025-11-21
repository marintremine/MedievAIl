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
                 range_: int, line_of_sight: int, speed: float, cooldown: float, x: int, y: int, bonus_attacks: dict, battle_model):
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
        self.cooldown = cooldown
        self.cooldown_timer = 0
        self.move_progress = 0
        self.action = Wait(self)
        self.bonus_attacks = bonus_attacks

    def is_alive(self) -> bool:
        return self.hp > 0
    
    def in_range(self, target: "Unit") -> bool:
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        return distance <= self.range

    def attack_target(self, target: "Unit") -> bool:
        if not self.is_alive() or not target.is_alive() or not self.in_range(target):
            return False
  
        # Décrémenter le cooldown à chaque tick
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1 * self.battle_model.delta_time
            return False
        
        # Effectuer l'attaque
        damage = self.attack - target.armor
        pierce_damage = self.attack - target.pierce_armor
        total_damage = max(damage, pierce_damage, 0)
        target.hp -= total_damage
        
        # Réinitialiser le cooldown
        self.cooldown_timer = self.cooldown
        return True

    def move(self, new_x: int, new_y: int) -> bool:
        """Déplace l'unité vers les coordonnées spécifiées"""
        if not self.is_alive() or not self.battle_model.is_in_map(new_x, new_y) or self.battle_model.is_obstacle_at(new_x, new_y):
            return False
        
        # distance = abs(new_x - self.x) + abs(new_y - self.y)
        # if distance == 0:
        #     self.move_progress = 0
        #     return False
    
        self.move_progress += self.speed * self.battle_model.delta_time
        
        if self.move_progress >= 1.0:
            self.x = new_x
            self.y = new_y
            self.move_progress -= 1.0 
            return True
        
        return False

    def __str__(self) -> str:
        return f"Unit({self.name}, HP: {self.hp}/{self.max_hp}, Pos: ({self.x}, {self.y}))"
    

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
            cooldown=3,
            x=x,
            y=y,
            bonus_attacks={},
            battle_model=battle_model   
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
            cooldown=1.8,
            x=x,
            y=y,
            bonus_attacks={},
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
            cooldown=2,
            x=x,
            y=y,
            bonus_attacks={},            
            battle_model=battle_model
        )
        self.accuracy = 0.85

    def attack_target(self, target) -> bool:
        """Attaque avec gestion de la précision"""
        if not self.is_alive() or not target.is_alive() or not self.in_range(target):
            return False
        
        # Décrémenter le cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= self.battle_model.delta_time
            return False
        
        # Effectuer l'attaque avec précision
        if random.random() <= self.accuracy:
            damage = self.attack - target.armor
            pierce_damage = self.attack - target.pierce_armor
            total_damage = max(damage, pierce_damage, 0)
            target.hp -= total_damage
        
        # Réinitialiser le cooldown même si raté
        self.cooldown_timer = self.cooldown
        return True


def unitFactory(unit_type, general, x, y, battle_model) -> Unit: # pyright: ignore[reportUndefinedVariable]
    unit_classes = {
        "pikeman": Pikeman,
        "knight": Knight,
        "crossbowman": Crossbowman
    }
    key = unit_type.lower()
    if key in unit_classes:
        return unit_classes[key](general, x, y, battle_model)
    else:
        raise ValueError(f"Unknown unit type: {key}")