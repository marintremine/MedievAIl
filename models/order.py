from __future__ import annotations


class Order:
    def __init__(self, unit: "Unit", battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        self.unit = unit
        self.battle_model = battle_model

    def action(self) -> None:
        pass   


class Move(Order):
    def __init__(self, unit: "Unit", x: int, y: int, battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit, battle_model)
        self.target_x = x
        self.target_y = y

    def action(self) -> None:

        path = self.battle_model.shortest_path(
            start=(self.unit.x, self.unit.y),
            end=(self.target_x, self.target_y)
        )

        if path is None:
            self.unit.action = Wait(self.unit)
            return
         
        next_x, next_y = path
        self.unit.move(next_x, next_y)
        
class Attack(Order) :
    def __init__(self, unit: "Unit", target: "Unit", battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit, battle_model)
        self.target = target

    def action(self) -> None:
        if not self.target.is_alive():
            self.unit.action = Wait(self.unit)
            return
        
        if self.unit.in_range(self.target):
            self.unit.attack_target(self.target)
        else:
            path = self.battle_model.shortest_path(
                start=(self.unit.x, self.unit.y),
                end=(self.target.x, self.target.y)
            )
            
            if path is None:
                self.unit.action = Wait(self.unit)
                return
            
            next_x, next_y = path
            self.unit.move(next_x, next_y)

class Wait(Order):
    def __init__(self, unit: "Unit") -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit, None)
        self.unit.direction = (0, 0)

    def action(self) -> None:
        pass