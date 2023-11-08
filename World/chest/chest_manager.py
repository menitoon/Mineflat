import pickle
import os
from settings import CHEST_SLOTS

class ChestManager:

  __slot__ = "inventory", "position"
  
  def __init__(self, position):
    self.position = position
    self.inventory = self.init_inventory()
    
  def init_inventory(self):
    # check if save exist
    PATH = f"LocalBlockData/{self.position['x']},{self.position['y']}.txt"
    if os.path.exists(PATH):
      # load inventory
      with open(PATH, "rb") as f:
        return pickle.load(f)
    else:
      # init inventory
      return [None] * CHEST_SLOTS