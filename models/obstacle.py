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