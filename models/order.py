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
        if len(path) > 2:
            next_x, next_y = path[1]
            self.unit.move(next_x, next_y)
        elif len(path) == 2:
            next_x, next_y = path[1]
            self.unit.move(next_x, next_y)
            self.unit.action = Wait(self.unit)  # Reached destination
        elif len(path) == 1:
            # Already at the target
            pass
        else:
            pass  # No valid path found; unit stays in place

class Attack(Order) :
    def __init__(self, unit: "Unit", target: "Unit", battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit, battle_model)
        self.target = target

    def action(self) -> None:
        if self.unit.can_attack():
            pass

        # self.unit.attack_target(self.target)

class Wait(Order):
    def __init__(self, unit: "Unit") -> None: # pyright: ignore[reportUndefinedVariable]
        super().__init__(unit, None)

    def action(self) -> None:
        pass