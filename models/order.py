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
        self.path = self.battle_model.shortest_path(
            start=(self.unit.x, self.unit.y),
            end=(self.target_x, self.target_y)
        )

    def action(self) -> None:
        if len(self.path) < 2:
            self.unit.action = Wait(self.unit)
            return
         
        next_x, next_y = self.path[1]

        if self.unit.move(next_x, next_y):
            self.path.pop(1)  # Remove the step if movement was successful
        
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
            if len(path) < 2:
                self.unit.action = Wait(self.unit)
                return
            
            next_x, next_y = path[1]
            
            if self.unit.move(next_x, next_y):
                pass  # Move successful, continue attacking next tick, we need to recalculate path et check range again

class Wait(Order):
    def __init__(self, unit: "Unit") -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit, None)

    def action(self) -> None:
        pass