from custom_class import block
from settings import TIME_GROW, BLOCKS
import random
import os

class Seed(block.Block):
  __slots__ = "canvas_owner", "char", "position", "name", "block_id", "groups", "layer", "time_grow", "chunk_loader"
  
  def __init__(
    self, canvas, char : str, position : dict,
    name : str, block_id : str, chunk_loader, layer=0 ,groups=[] 
  ):
  
    self.register_info(canvas, char, position, name , groups, layer)
    self.block_id = block_id
    self.chunk_loader = chunk_loader
    self.chunk_loader.entity_to_update.add(self)
    self.time_grow = random.randrange(TIME_GROW[0], TIME_GROW[1]) * 60
    # check if value already exists if yes read from that
    self.add_chunk_info()
  
  def update(self, time_in_game):

    time_left = self.time_grow - time_in_game
    
    if time_left <= 0:
      print(f"GROWN : {self.name}")
      self.chunk_loader.add_block(BLOCKS["plant_grown"], self.position)
      self.kill()
    else:
      print(time_left)

  def kill(self):
    self.chunk_loader.entity_to_update.remove(self)
    super().kill()