import oz_engine as oz
from settings import *


class Block(oz.Sprite):
  __slots__ = "canvas_owner", "char", "position", "name", "block_id", "groups", "layer", "chunk_loader"
  
  def __init__(
    self, canvas, char : str, position : dict,
    name : str, block_id : str, chunk_loader, layer=0 ,groups=[]
  ):
    
    self.register_info(canvas, char, position, name , groups, layer)
    self.block_id = block_id
    self.chunk_loader = chunk_loader
    self.add_chunk_info()
  
  def add_chunk_info(self):
    # add data to chunk
    chunk_id = self.chunk_loader.get_chunk_id(self.position)
    self.chunk_loader.chunk_loaded[chunk_id]["data"].add(self)

  def kill(self):
    chunk_id = self.chunk_loader.get_chunk_id(self.position)
    self.chunk_loader.chunk_to_update.add(chunk_id)
    self.chunk_loader.chunk_loaded[chunk_id]["data"].remove(self)
    super().kill()


  def mined(self):
    self.kill()
