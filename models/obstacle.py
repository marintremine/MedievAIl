from models.unit import Object

class Obstacle(Object):
  def __init__(self, x: int, y: int,type_="Wall"): #default obstacle is Wall
      super().__init__(x, y)
      self.type = type_ 
  def __str__(self):
        return f"Obstacle({self.type}) at ({self.x}, {self.y})"