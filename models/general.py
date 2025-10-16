from models.unit import Unit

class General:
    def __init__(self, name: str, my_units: list[Unit]):
        self.name = name
        self.my_units = my_units

    def decide(self) -> None:
        pass


class Daft(General):
    def __init__(self, name: str, my_units: list[Unit]):
        super().__init__(name, my_units)

    def decide(self) -> None:
        pass

class BrainDead(General):
    def __init__(self, name: str, my_units: list[Unit]):
        super().__init__(name, my_units)

    def decide(self) -> None:
        pass
