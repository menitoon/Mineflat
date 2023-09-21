import oz_engine as oz
import custom_class as cc
from settings import BLOCKS

class Player(oz.Sprite):

    __slots__ = "canvas_owner", "char", "position", "name", "group", "layer", "direction", "reach", "camera", "inventory", "is_in_shop", "is_near_shop", "coin", "block_in_hand", "clip", "move_unit"

    def __init__(
      self, canvas_owner, char : str, position : dict,
      name : str, camera, inventory, coin, group=[], layer : int=0
    ):

        self.register_info(canvas_owner, char, position, name, group, layer)

        # declare other attribute
        self.direction = {"x" : 1, "y" : 0}
        self.reach = 3
        self.camera = camera
        self.inventory = inventory
        self.is_near_shop = False
        self.is_in_shop = False
        self.coin = coin
        self.block_in_hand = "air"
        self.clip = False
        self.move_unit = 1
    
    def move(self, action : str):

        if self.is_in_shop:
          return
      
        if action == "🔼":
            
            if not "wall" in self.get_colliding_groups(
              {"x": self.position["x"], "y": self.position["y"] - self.move_unit}
            ) or self.clip:
                self.camera.change_y(-self.move_unit)
                self.change_y(-self.move_unit)
                

        elif action == "🔽":
            if not "wall" in self.get_colliding_groups(
              {"x": self.position["x"], "y": self.position["y"] + self.move_unit}
            ) or self.clip:
                self.camera.change_y(self.move_unit)
                self.change_y(self.move_unit)
                

        elif action == "◀":
            if not "wall" in self.get_colliding_groups(
              {"x": self.position["x"] - self.move_unit, "y": self.position["y"]}
            ) or self.clip:
                self.camera.change_x(-self.move_unit)
                self.change_x(-self.move_unit)
                

        elif action == "▶":
            if not "wall" in self.get_colliding_groups(
              {"x": self.position["x"] + self.move_unit, "y": self.position["y"]}
            ) or self.clip:
                self.camera.change_x(self.move_unit)
                self.change_x(self.move_unit)

    def is_shop_near(self):
      surrondings = (
        (-1, 0), (1, 0), (0, 1), (0, -1),
        (-1, 1), (1, 1), (-1, -1), (1, -1)
      )

      for around_position in surrondings:
        around_position = {
          "x" : around_position[0] + self.position["x"],
          "y" : around_position[1] + self.position["y"]
                          }
        
        if "shop" in self.get_colliding_groups(around_position):
          return around_position

      return None
          
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
      print(self.direction)

    def get_turn_str(self):

      tuple_direction = (self.direction["x"], self.direction["y"])
      
      str_dict = {
        (-1, 0) : "⬅",
        (1, 0)  : "⮕",
        (0, 1)  : "⬇",
        (0, -1) : "⬆",
      }

      return str_dict[tuple_direction]


    def build(self, chunk_loader):

      if self.block_in_hand == "air" or not self.block_in_hand in self.inventory:
        return
    
      build_destination = {
        "x": self.position["x"] + self.direction["x"],
        "y": self.position["y"] + self.direction["y"]
                        }
  
      block_destination = self.canvas_owner.get_elements(build_destination)
      print(block_destination)
      if block_destination != []:
        # if there is a block return
        return False

      chunk_id = chunk_loader.get_chunk_id(build_destination)  
      # get block chosen to build
      block_type_placed = self.block_in_hand
      # get char of block chosen
      block_type_str = BLOCKS[block_type_placed]["char"]
      # groups
      block_type_groups = BLOCKS[block_type_placed]["group"]
      
      # place block in canvas data
      block = cc.Block(self.canvas_owner, block_type_str, build_destination, block_type_placed, block_type_placed, groups=block_type_groups)
      chunk_loader.chunk_loaded[chunk_id]["data"].add(block)
      chunk_loader.chunk_to_update.add(chunk_id)
      # remove 1 block from inventory
      self.inventory[block_type_placed] -= 1
      if self.inventory[block_type_placed] == 0:
        # if no block left remove key from inventory
        del self.inventory[block_type_placed]
      return True



    def mine(self, chunk_loader, player_to_update):
      block_selected = ""
      block_pos = self.position.copy()
      reach_left = self.reach
  
      while (reach_left > 0) and (len(block_selected) < 1):
        block_pos["x"] += self.direction["x"]
        block_pos["y"] += self.direction["y"]
        block_selected = self.canvas_owner.get_elements(block_pos)
        reach_left -= 1

       
      
      if len(block_selected) == 0:
        # if no block to mine
        # don't mine
        return
      
      block_selected = self.canvas_owner.get_sprite(block_selected[0])
      if "no-mine" in block_selected.groups:
        # block can't be mined
        return
      
      chunk_id = chunk_loader.get_chunk_id(block_pos)
      chunk_loader.chunk_to_update.add(chunk_id)
      player_to_update.add(self)
      block_type = block_selected.block_id
      chunk_loader.chunk_loaded[chunk_id]["data"].remove(block_selected)
      block_selected.kill()
      self.inventory[block_type] = self.inventory.get(block_type, 0) + 1
    
