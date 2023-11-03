from custom_class import block
from settings import TIME_GROW, BLOCKS
import random
import os
import pickle

class Seed(block.Block):
  __slots__ = "canvas_owner", "char", "position", "name", "block_id", "groups", "layer", "time_grow", "chunk_loader", "game_time"
  
  def __init__(
    self, canvas, char : str, position : dict,
    name : str, block_id : str, chunk_loader, layer=0 ,groups=[] 
  ):
    print("CHECK : ", issubclass(self.__class__, block.Block) )
    self.register_info(canvas, char, position, name , groups, layer)
    self.block_id = block_id
    self.chunk_loader = chunk_loader
    self.chunk_loader.entity_to_update.add(self)
    self.time_grow = random.randrange(TIME_GROW[0], TIME_GROW[1]) * 60
    self.game_time = chunk_loader.game_time
    # check if value already exists if yes read from that
    if os.path.isfile(f"LocalBlockData/{self.position['x']},{self.position['y']}.txt"):
      self.load_state()
    self.add_chunk_info()
  
  def update(self):

    time_left = self.time_grow - self.game_time.time_in_game
    
    if time_left <= 0:
      print(f"GROWN : {self.name}")
      self.grown()
      return self.position
    else:
      print(time_left)
  
  def save_state(self):
    save_file = open(f"LocalBlockData/{self.position['x']},{self.position['y']}.txt", "wb")
    
    save_data = {
      "time_grow" : self.time_grow - self.game_time.time_in_game
    }
    
    pickle.dump(save_data, save_file)
    save_file.close()

  def load_state(self):
    save_file = open(f"LocalBlockData/{self.position['x']},{self.position['y']}.txt", "rb")
    data = pickle.load(save_file)
    self.time_grow = data["time_grow"]
      
  def kill(self):
    self.save_state()
    self.chunk_loader.entity_to_update.remove(self)
    super().kill()

  def grown(self):
    self.chunk_loader.add_block(BLOCKS["plant_grown"], self.position)
    # delete file data from LocalBlockData
    os.remove(f"LocalBlockData/{self.position['x']},{self.position['y']}.txt")
    self.kill()