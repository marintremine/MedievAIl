from models.general import General
from models.order import Wait


class Object:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Unit(Object):
    def __init__(self, name: str, general: General, hp: int, attack: int, armor: int, pierce_armor: int,
                 range_: int, line_of_sight: int, speed: float, cooldown: float, x: int, y: int, bonus_attacks: dict):
        super().__init__(x, y)
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
        self.move_progress = 0
        self.action = Wait(self)
        self.bonus_attacks = bonus_attacks

    def is_alive(self) -> bool:
        return self.hp > 0

    def attack_target(self, target: "Unit") -> None:
        pass

    def move(self, x: int, y: int) -> None:
        pass

    def __str__(self) -> str:
        return f' TODO '
    

class Pikeman(Unit):
    def __init__(self, general: General, x: int, y: int):
        super().__init__(
            name="Pikeman",
            general=general,
            hp=55,
            max_hp=55,
            attack=4,
            armor=0,
            pierce_armor=0,
            range_=0,
            line_of_sight=4,
            speed=1,
            cooldown=3
            bonus_attacks={
                Pikeman: 
            }
        )




class Knight(Unit):
    def __init__(self, general:General, x:int, y:int):
        super().__init__(
            name="Knight",
            general=general,
            hp=100,
            max_hp=100,
            attack=10,
            armor=2,
            pierce_armor=2,
            range_=0,
            line_of_sight=4,
            speed=1.35,
            cooldown=1.8
        )


class Crossbowman(Unit):
    def __init__(self, general:General, x:int, y:int):
        super().__init__(
            name="Crossbowman",
            general=general,
            hp=35,
            max_hp=35,
            attack=5,
            armor=0,
            pierce_armor=0,
            range_=5,
            line_of_sight=7,
            speed=0.96,
            cooldown=2
        )
        self.accuracy = 0.85
