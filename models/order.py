from __future__ import annotations
class Order:
    def __init__(self, unit: "Unit") -> None:
        self.unit = unit

    def action(self) -> None:
        pass

class Move(Order):
    def __init__(self, unit: "Unit", x: int, y: int) -> None:
        super().__init__(unit)
        self.target_x = x
        self.target_y = y

    def action(self) -> None:
        self.unit.move(self.target_x, self.target_y)

class Attack(Order) :
    def __init__(self, unit: "Unit", target: "Unit") -> None:
        super().__init__(unit)
        self.target = target

    def action(self) -> None:
        self.unit.attack_target(self.target)

class Wait(Order):
    def __init__(self, unit: "Unit"):
        super().__init__(unit)

    def action(self) -> None:
        pass