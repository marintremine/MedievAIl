class Unit:
    def __init__(self, name, player, hp, attack, armor, pierce_armor,
                 range_, line_of_sight, speed, build_time, reload_time):
        self.name = name
        self.player = player
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.armor = armor
        self.pierce_armor = pierce_armor
        self.range = range_
        self.line_of_sight = line_of_sight
        self.speed = speed
        self.build_time = build_time
        self.reload_time = reload_time
        self.cooldown = 0
        self.position = (0, 0)
        self.move_progress = 0

    def is_alive(self):
        return self.hp > 0
    

    def __str__(self):
        return f'{self.name}({self.player}){str(id(self))[-2:]}'

class Pikeman(Unit):
    def __init__(self, player):
        super().__init__(
            name="Pikeman",
            player=player,
            hp=55,
            attack=4,
            armor=0,
            pierce_armor=0,
            range_=0,
            line_of_sight=4,
            speed=1,
            build_time=22,
            reload_time=3
        )

class Knight(Unit):
    def __init__(self, player):
        super().__init__(
            name="Knight",
            player=player,
            hp=100,
            attack=10,
            armor=2,
            pierce_armor=2,
            range_=0,
            line_of_sight=4,
            speed=1.35,
            build_time=30,
            reload_time=1.8
        )


class Crossbowman(Unit):
    def __init__(self, player):
        super().__init__(
            name="Crossbowman",
            player=player,
            hp=35,
            attack=5,
            armor=0,
            pierce_armor=0,
            range_=5,
            line_of_sight=7,
            speed=0.96,
            build_time=27,
            reload_time=2
        )
        self.accuracy = 0.85
