from __future__ import annotations

class General:
    def __init__(self, name: str, my_units: list["Unit"]):
        self.name = name
        self.my_units = my_units

    def decide(self) -> None:
        pass


class Daft(General):
    def __init__(self):
        super().__init__("Daft", [])
    def decide(self) -> None:
        pass

class BrainDead(General):
    def __init__(self):
        super().__init__("BrainDead", [])

    def decide(self) -> None:
        pass


def generalFactory(general_type: str) -> General:
    general_classes = {
        "daft": Daft,
        "braindead": BrainDead
    }
    key = general_type.lower()
    if key in general_classes:
        return general_classes[key]()
    else:
        raise ValueError(f"Unknown general type: {key}")