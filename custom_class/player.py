import oz_engine as oz


class Player(oz.Sprite):

    __slots__ = "canvas_owner", "char", "position", "name", "group", "layer", "direction", "reach", "camera", "inventory"

    def __init__(
      self, canvas_owner, char : str, position : dict,
      name : str, camera, inventory, group=[], layer : int=0
    ):

        self.register_info(canvas_owner, char, position, name, group, layer)

        # declare other attribute
        self.direction = {"x" : 1, "y" : 0}
        self.reach = 3
        self.camera = camera
        self.inventory = {}
        
        
  
    def move(self, action : str):
      
        if action == "🔼":
            
            if not "wall" in self.get_colliding_groups(
              {"x": self.position["x"], "y": self.position["y"] - 1}
            ):
                self.camera.change_y(-1)
                self.change_y(-1)
                

        elif action == "🔽":
            if not "wall" in self.get_colliding_groups(
              {"x": self.position["x"], "y": self.position["y"] + 1}
            ):
                self.camera.change_y(1)
                self.change_y(1)
                

        elif action == "◀":
            if not "wall" in self.get_colliding_groups(
              {"x": self.position["x"] - 1, "y": self.position["y"]}
            ):
                self.camera.change_x(-1)
                self.change_x(-1)
                

        elif action == "▶":
            if not "wall" in self.get_colliding_groups(
              {"x": self.position["x"] + 1, "y": self.position["y"]}
            ):
                self.camera.change_x(1)
                self.change_x(1)

    def turn(self):
      DIRECTION = (
        {"x" : 1, "y" : 0},
        {"x" : 0, "y" : 1},
        {"x" : -1, "y" : 0},
        {"x" : 0, "y" : -1},
                  )

      index = DIRECTION.index(self.direction)
      index -= 1
      if index > 3:
        index = 0

      self.direction = DIRECTION[index]

    def get_turn_str(self):

      tuple_direction = (self.direction["x"], self.direction["y"])
      
      str_dict = {
        (-1, 0) : "⬅",
        (1, 0)  : "⮕",
        (0, 1)  : "⬇",
        (0, -1) : "⬆",
      }

      return str_dict[tuple_direction]
