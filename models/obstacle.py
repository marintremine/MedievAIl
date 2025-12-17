from models.unit import Object

class Obstacle(Object):
  def __init__(self, x: int, y: int,sizeX: int,sizeY: int, battle_model, type_="Bush" ): #default obstacle is Wall
      super().__init__(x, y, battle_model)
      self.type = type_
      self.sizeX = sizeX
      self.sizeY = sizeY

  def __str__(self):
        return f"Obstacle({self.type}) at ({self.x}, {self.y})"
  
  def to_dict(self):
    return {
        "type": self.type,
        "x": self.x,
        "y": self.y,
        "sizeX": self.sizeX,
        "sizeY": self.sizeY,
    }

class Bush(Obstacle):
    def __init__(self, x: int, y: int, battle_model):
        super().__init__(
            type_ = "Bush",
            x = x,
            y = y,
            sizeX = 5,
            sizeY = 5,
            battle_model = battle_model
        )


class Rock(Obstacle):
    def __init__(self, x: int, y: int, battle_model):
        super().__init__(
            type_ = "Rock",
            x = x,
            y = y,
            sizeX = 10,
            sizeY = 10,
            battle_model = battle_model
        )

class Tree(Obstacle):
    def __init__(self, x: int, y: int, battle_model):
        super().__init__(
            type_ = "Tree",
            x = x,
            y = y,
            sizeX = 3,
            sizeY = 3,
            battle_model = battle_model
        )


def ObstacleFactory(obs_type: str, x: int, y: int, battle_model) -> Obstacle:
    obstacle_classes = {
        "bush": Bush,
        "rock": Rock,
        "tree": Tree,
    }
    key = obs_type.lower()
    if key in obstacle_classes:
        return obstacle_classes[key](x, y, battle_model)
    else:
        raise ValueError(f"Unknown obstacle type: {key}")

