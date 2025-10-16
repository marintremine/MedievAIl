class BattleModel:
    def __init__(self)->None:
        self.general_1 = None
        self.general_2 = None
        self.running = False
        self.map_width = None
        self.map_height = None
        self.list_objects = []

    def load(self, scenario_file:str)->None:
        pass

    def update(self)->None:
        pass

    def start(self)->None:
        pass

    def stop(self)->None:
        pass

    def restart(self)->None:
        pass

    def pause(self)->None:
        pass

    def save(self, scenario_file:str)->None:
        pass
