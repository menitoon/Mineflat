import oz_engine as oz
import random
from settings import *



class Block(oz.Sprite):
  __slots__ = "canvas_owner", "char", "position", "name", "block_id", "groups", "layer", 
  
  def __init__(
    self, canvas, char : str, position : dict,
    name : str, block_id : str, layer=0 ,groups=[]
  ):
    
    self.register_info(canvas, char, position, name , groups, layer)
    self.block_id = block_id


 
