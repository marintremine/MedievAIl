from models.unit import Object

class Obstacle(Object):
  def __init__(self, x: int, y: int, battle_model, type_="Wall" ): #default obstacle is Wall
      super().__init__(x, y, battle_model)
      self.type = type_ 
  def __str__(self):
        return f"Obstacle({self.type}) at ({self.x}, {self.y})"
  
  def to_dict(self):
    return {
        "type": "obstacle",
        "x": self.x,
        "y": self.y,
    }
  

def ObstacleFactory(obs_type: str, x: int, y: int, battle_model) -> Obstacle:
    obstacle_classes = {
        "obstacle": Obstacle,
    }
    key = obs_type.lower()
    if key in obstacle_classes:
        return obstacle_classes[key](x, y, battle_model, obs_type)
    else:
        raise ValueError(f"Unknown obstacle type: {key}")

