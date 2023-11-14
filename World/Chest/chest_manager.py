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
      with open(PATH, "rb") as file:
        return pickle.load(file)
    else:
      # init inventory
      return [None] * CHEST_SLOTS
  
  def save_inventory(self):
    PATH = f"LocalBlockData/{self.position['x']},{self.position['y']}.txt"
    with open(PATH, "wb") as file:
      pickle.dump(self.inventory, file)
    
  def add_item(self, slot, item, amount):

    amount = int(amount)
    
    if self.inventory[slot] is None:
      self.inventory[slot] = {item : amount}
      self.save_inventory()
      return f"You added {amount} {item} to the chest."
    elif not self.inventory[slot] is None:
      # if the same item is in that slot add more
      self.inventory[slot][item] += amount
      self.save_inventory()
      return f"You added {amount} {item} to the chest."
    else:
      # if isn't the same item then output a warning
      # message and refuse input
      current_item = list(self.inventory[slot].keys())[0]
      return f"**⚠️ Can't drop {item} because {current_item} is already in this slot\nPlease drop this item in a slot that is empty or has got the same item type.**"


  def remove_item(self, slot, amount):
    
    amount = int(amount)
    item = list(self.inventory[slot].keys())[0]
    
    if self.inventory[slot] is None:
      return f"**️You can't take items, since slot {slot} is empty.**"
    elif (self.inventory[slot][item] - amount) >= 0:
      
      self.inventory[slot][item] -= amount
      if self.inventory[slot][item] == 0:
        self.inventory[slot] = None
      self.save_inventory()
      return f"You took {amount} {item} from the chest."