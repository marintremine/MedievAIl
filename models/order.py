from __future__ import annotations
import random


class Order:
    def __init__(self, unit: "Unit") -> None: # pyright: ignore[reportUndefinedVariable]
        self.unit = unit

    def action(self) -> None:
        if not self.unit.is_alive():
            return



class Move(Order):
    def __init__(self, unit: "Unit", x: int, y: int) -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit)
        self.target_x = x
        self.target_y = y

    def action(self) -> None:
        super().action()

        path = self.unit.battle_model.shortest_path(self.unit,
            start=(self.unit.x, self.unit.y),
            end=(self.target_x, self.target_y)
        )

        if path is None:
            self.unit.order = Wait(self.unit)
            return
        
        next_x, next_y = path
        self.unit.move(next_x, next_y)

         
class Attack(Order) :
    def __init__(self, unit: "Unit", target: "Unit") -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit)
        self.target = target

    def action(self) -> None:
        super().action()

        if not self.target.is_alive():
            self.unit.order = Wait(self.unit)
            return
        
        if self.unit.in_range(self.target):
            self.unit.attack_target(self.target)
        else:
            path = self.unit.battle_model.shortest_path(self.unit,
                start=(self.unit.x, self.unit.y),
                end=(self.target.x, self.target.y)
            )
            
            if path is None:
                self.unit.order = Wait(self.unit)
                return
            
            next_x, next_y = path
            self.unit.move(next_x, next_y)
        


class Wait(Order):
    def __init__(self, unit: "Unit") -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit)
        self.unit.currentAction = "stand"

    def action(self) -> None:
        super().action()
        pass

class Defense(Order):
    def __init__(self, unit: "Unit") -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit)
        self.unit.currentAction = "stand"

    def action(self) -> None:
        super().action()

        enemies_in_range = self.unit.enemies_in_range()
        if len(enemies_in_range) > 0:
            target = enemies_in_range[0]
            self.unit.attack_target(target)
            return
        enemies_in_sight = self.unit.enemies_in_sight()
        if len(enemies_in_sight) > 0:
            target = enemies_in_sight[0]
            path = self.unit.battle_model.shortest_path(
                self.unit,
                start=(self.unit.x, self.unit.y),
                end=(target.x, target.y)
            )
            if path is None:
                return
            next_x, next_y = path
            self.unit.move(next_x, next_y)

        