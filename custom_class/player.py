import oz_engine as oz
import custom_class as cc
from settings import BLOCKS
import random

class Player(oz.Sprite):

    __slots__ = "canvas_owner", "char", "position", "name", "group", "layer", "direction", "reach", "camera", "inventory", "is_in_table", "table", "coin", "block_in_hand", "clip", "move_unit", "effect"

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
        self.is_in_table = False
        self.coin = coin
        self.block_in_hand = "air"
        self.clip = False
        self.move_unit = 1
        self.effect = {}
        self.table = None
  
    def move(self, action : str):

        if self.is_in_table:
          return
      
        if action == "🔼":
            move_unit = self.get_move_unit_for_direction({"x" : 0, "y" : -1})
            self.camera.change_y(-move_unit)
            self.change_y(-move_unit)
                
        elif action == "🔽":
          move_unit = self.get_move_unit_for_direction({"x" : 0, "y" : 1})
          self.camera.change_y(move_unit)
          self.change_y(move_unit)
                
        elif action == "◀":
          move_unit = self.get_move_unit_for_direction({"x" : -1, "y" : 0})
          self.camera.change_x(-move_unit)
          self.change_x(-move_unit)
                
        elif action == "▶":
          move_unit = self.get_move_unit_for_direction({"x" : 1, "y" : 0})
          self.camera.change_x(move_unit)
          self.change_x(move_unit)

        
        # check if has speed effect
        speed_key = self.effect.get("speed")
        if not speed_key is None:
          # if key exist remove one from effect until it dissapear
          self.effect["speed"] = speed_key - 1
          if self.effect["speed"] == 0:
            del self.effect["speed"]
            self.move_unit = 1
  
  
     
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

    def get_position_direction(self):
      return {
        "x": self.position["x"] + self.direction["x"],
        "y": self.position["y"] + self.direction["y"]
                        }
    
    def build(self, chunk_loader):

      if self.block_in_hand == "air" or not self.block_in_hand in self.inventory:
        return
    
      build_destination = self.get_position_direction()
  
      block_destination = self.canvas_owner.get_elements(build_destination)
      
      if block_destination != []:
        # if there is a block return
        return False
      
      chunk_id = chunk_loader.get_chunk_id(build_destination)  
      # get block chosen to build
      block_type_placed = self.block_in_hand
      self.lose_item(block_type_placed, 1)
      # place block in canvas data
      chunk_loader.add_block(BLOCKS[block_type_placed], build_destination)
      
      
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
        return None
      for block in block_selected:
        if isinstance(block, cc.Block):
          block_selected = block
          break
      block_selected = self.canvas_owner.get_sprite(block_selected[0])
      if "no-mine" in block_selected.groups:
        # block can't be mined
        return

      self.add_block_inventory(block_selected.block_id)
      player_to_update.add(self)
      block_selected.mined()
      return block_pos

    def add_block_inventory(self, block_type):
      block_info = BLOCKS[block_type]
      block_drop = block_info.get("drop")
      if not block_drop is None:
        for drop, amount in block_drop.items():
          if isinstance(amount, tuple):
            amount = random.randint(amount[0], amount[1])
          self.inventory[drop] = self.inventory.get(drop, 0) + amount

      self.inventory[block_type] = self.inventory.get(block_type, 0) + 1

    def get_move_unit_for_direction(self, direction : dict):
      # get how many unit the player can move before he hits a wall
      # or has no more unit to move

      # if can clip no check needed
      if self.clip:
        return self.move_unit
      
      for i in range(1, self.move_unit + 1):
        destination = {
          "x" : self.position["x"] + direction["x"] * i,
          "y" : self.position["y"] + direction["y"] * i
                      }
        colliding = self.canvas_owner.get_elements(destination)
        for collision in colliding:
          if "wall" in self.canvas_owner.get_sprite(collision).groups:
            return i - 1
      return self.move_unit

    def kill(self):
      self.camera.kill()
      super().kill()


    def lose_item(self, item, amount):
      # remove 1 block from inventory
      self.inventory[item] -= amount
      if self.inventory[item] == 0:
        # if no block left remove key from inventory
        del self.inventory[item]

    