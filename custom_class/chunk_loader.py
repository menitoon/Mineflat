import os
import settings
import math
import perlin as pl
from .block import Block
from settings import *

SIZE = settings.PERLIN_SIZE

class ChunkLoader:
    __slots__ = "size", "perl", "chunk_loaded" , "chunk_to_update", "canvas_owner"
  
    def __init__(self, canvas_owner, size : tuple):
        self.size = size
        self.perl = pl.PerlinNoise((SIZE[0], SIZE[1]))
        self.perl.SEED = get_seed()
        self.chunk_loaded = {}
        self.chunk_to_update = set()
        self.canvas_owner = canvas_owner
  
    def load_surroundings(self, position : dict, author):
      surroundings = (
          (0, 0), (-1, 0), (-1, 1), (0, 1),
          (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)
        )

      chunk_id = self.get_chunk_id(position)
      
      for pos in surroundings:
        chunk_load = (pos[0] + chunk_id[0], pos[1] + chunk_id[1])
        self.load_chunk(chunk_load ,author)

    def get_chunk_id(self, position : dict):
      return (
        math.floor(position["x"] / self.size[0]), 
        math.floor(position["y"] / self.size[1])
      )
  
    
    def add_block(self, block_info, position : dict):

      
      # define block type
      char = block_info["char"]
      name_type = block_info["name"]
      group = block_info["group"]
  
      block = Block(self.canvas_owner, char, position, name_type, name_type, groups=group)

      # add data to chunk
      chunk_id = self.get_chunk_id(position)
      self.chunk_loaded[chunk_id]["data"].add(block)

  
    def load_and_unload_chunks(self, pos : dict, new_pos : dict, author):
        
        chunk_id = self.get_chunk_id(pos)
        new_chunk_id = self.get_chunk_id(new_pos)

        # gives the chunk direction you moved in 
        direction_chunk = (new_chunk_id[0] - chunk_id[0], 
                           new_chunk_id[1] - chunk_id[1])

        if direction_chunk == (0, 0):
          return
      
        if direction_chunk == (1, 0):
            
            self.unload_chunk((chunk_id[0] - 1, chunk_id[1]) , author)
            self.unload_chunk((chunk_id[0] - 1, chunk_id[1] + 1), author)
            self.unload_chunk((chunk_id[0] - 1, chunk_id[1] - 1), author)

            self.load_chunk((new_chunk_id[0] + 1, new_chunk_id[1]), author)
            self.load_chunk((new_chunk_id[0] + 1, new_chunk_id[1] + 1), author)
            self.load_chunk((new_chunk_id[0] + 1, new_chunk_id[1] - 1), author)
            
        elif direction_chunk == (-1, 0):
            
            self.unload_chunk((chunk_id[0] + 1, chunk_id[1]), author)
            self.unload_chunk((chunk_id[0] + 1, chunk_id[1] + 1), author)
            self.unload_chunk((chunk_id[0] + 1, chunk_id[1] - 1), author)

            self.load_chunk((new_chunk_id[0] - 1, new_chunk_id[1]), author)
            self.load_chunk((new_chunk_id[0] - 1, new_chunk_id[1] + 1), author)
            self.load_chunk((new_chunk_id[0] - 1, new_chunk_id[1] - 1), author)
          
        elif direction_chunk == (0, 1):
            
            self.unload_chunk((chunk_id[0] , chunk_id[1] - 1), author)
            self.unload_chunk((chunk_id[0] - 1, chunk_id[1] - 1), author)
            self.unload_chunk((chunk_id[0] + 1, chunk_id[1] - 1), author)

            self.load_chunk((new_chunk_id[0] , new_chunk_id[1] + 1), author)
            self.load_chunk((new_chunk_id[0] + 1, new_chunk_id[1] + 1), author)
            self.load_chunk((new_chunk_id[0] - 1, new_chunk_id[1] + 1), author)
        else :
          # case (-1, 0)
            
            self.unload_chunk((chunk_id[0] , chunk_id[1] + 1), author)
            self.unload_chunk((chunk_id[0] - 1, chunk_id[1] + 1), author)
            self.unload_chunk((chunk_id[0] + 1, chunk_id[1] + 1), author)

            self.load_chunk((new_chunk_id[0] , new_chunk_id[1] - 1), author)
            self.load_chunk((new_chunk_id[0] + 1, new_chunk_id[1] - 1), author)
            self.load_chunk((new_chunk_id[0] - 1, new_chunk_id[1] - 1), author)


    def unload_chunk(self, chunk_id, author):

        self.chunk_loaded[chunk_id]["players"].remove(author)
      
        if len(self.chunk_loaded[chunk_id]["players"]) > 0:
          return
              
        for b in self.chunk_loaded[chunk_id]["data"]:
            b.kill()

        del self.chunk_loaded[chunk_id]

      
    def read_chunk(self, path, position):

      print(path)
      
      # Get chunk data from path
      chunk_data = open(path, "r")
      chunk_position = (position[0] * self.size[0], position[1] * self.size[1])

      chunk_str = chunk_data.read()
      
      pos_test = []
      
      x = 0
      y = 0

      amount = ""
      block_type = ""

      # read line per line
      for char in chunk_str:

        if char.isnumeric():
          amount += char

        elif char == ";":
          
          int_amount = int(amount)
          
          if block_type != "air":
            # get data of block
            block_type = BLOCKS[block_type]
            
            for a in range(int_amount):
              pos_placement = {"x": chunk_position[0] + x, "y": chunk_position[1] + y}
              self.add_block(block_type, pos_placement)
              x += 1
              if x == self.size[0]:
                x = 0
                y += 1
              
            amount = ""
            block_type = ""
          
          else:
            
            y += math.floor((int_amount + x) / self.size[0]) 
            x = (int_amount + x) % self.size[0]
            amount = ""
            block_type = ""
            
        else:
          block_type += char

  
    def load_chunk(self, position : list, author):

        print(position)
        
        self.chunk_loaded.setdefault(position, {"players" : set(), "data" : set()} )
        self.chunk_loaded[position]["players"].add(author)
        
      
        if len(self.chunk_loaded[position]["players"]) > 1:
          return
        
        # check if chunks has already been generated
        path = f"Chunks/{position[0]},{position[1]}.txt"
        
        if os.path.isfile(path):
            # Open chunk
            self.read_chunk(path, position)
        else:
          # Generate new chunk
          self.generate_chunk(position)
    
  
  
    def generate_chunk(self, position : list):
      
        amount = 0
       
      
        chunk_position = (
          position[0] * self.size[0], position[1] * self.size[1]
        )
      
        save_chunk = ""
        last_block = ""
        new_block = ""
        block_counter = -1

        new_block = Block.define_block(self.perl.get_perlin_at(chunk_position), chunk_position)
        # check if is air block
        new_block = "air" if new_block is None else new_block["name"]
        last_block = new_block

        for y in range(self.size[1]):
            for x in range(self.size[0]):
                
                pos_placement = (x + chunk_position[0], y + chunk_position[1])
              
                if new_block != last_block:
                    save_chunk += f"{block_counter}{last_block}"
                    block_counter = 0
                    save_chunk += ";"
                
                last_block = new_block

                value = self.perl.get_perlin_at(pos_placement)
                block_info = Block.define_block(value, pos_placement)
                if not block_info is None:
                  # solid block
                  pos_dict = {"x" : pos_placement[0], "y" : pos_placement[1]}
                  self.add_block(block_info, pos_dict)
                  new_block = block_info["name"]
                else:
                  new_block = "air"
                

                block_counter += 1
                amount += 1

        
        save_chunk += f"{block_counter}{last_block};"
        # adds backspace at the end of the line
        
        file_chunk = open(f"Chunks/{position[0]},{position[1]}.txt", "w")
        file_chunk.write(save_chunk)
        #file_chunk.write("your mom :")
        file_chunk.close()
        
        self.perl.reset_gradient_cache()


    def reset_data(self):
      for f in os.listdir("Chunks"):
        os.remove(f"Chunks/{f}")
      for d in os.listdir("PlayerData"):
        os.remove(f"PlayerData/{d}")
        

      
    def save_chunk(self, chunk_id):

      save_chunk = ""
      last_block = ""
      new_block = ""
      block_counter = -1

      chunk_id_pos = (
                 chunk_id[0] * self.size[0],
                 chunk_id[1] * self.size[1]
      )

      block = self.canvas_owner.get_elements(
            {
              "x": chunk_id_pos[0],
              "y": chunk_id_pos[1]
            }
          )

      
      new_block = "air"
      if len(block) != 0:
          for b in block:
            block_save = self.canvas_owner.get_sprite(b)
            if  isinstance(block_save, Block):
              new_block = block_save.block_id
              
            
            
      
      last_block = new_block
      
      for y in range(self.size[1]):
        for x in range(self.size[0]):
          block = self.canvas_owner.get_elements(
            {
              "x": x + chunk_id_pos[0],
              "y": y + chunk_id_pos[1]
            }
          )

          
          
          if new_block != last_block:
                    save_chunk += f"{block_counter}{last_block};"
                    block_counter = 0
                    
                
          last_block = new_block

          new_block = "air"
          if len(block) != 0:
              for b in block:
                block_save = self.canvas_owner.get_sprite(b)
                if  isinstance(block_save, Block):
                  new_block = block_save.block_id
          
              

          block_counter += 1

      save_chunk += f"{block_counter + 1}{last_block}"
      
      
      file_chunk = open(f"Chunks/{chunk_id[0]},{chunk_id[1]}.txt", "w")
      file_chunk.write(save_chunk)
      file_chunk.close()