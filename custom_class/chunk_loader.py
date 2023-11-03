import os
import settings
import math
from perlin import PerlinNoise
from .block import *
from .generation import *
from settings import *
from .player_loader import *
import SpecialBlock as sb

SIZE = settings.PERLIN_SIZE

class ChunkLoader:
    __slots__ = "size", "chunk_loaded" , "chunk_to_update", "canvas_owner", "fractal", "perlin", "perlin_plant", "entity_to_update", "game_time"
  
    def __init__(self, canvas_owner, size : tuple, fractal : int, game_time):
        self.size = size
        # contains all different perlin noise
        self.perlin = PerlinNoise(SIZE)
        self.perlin.SEED = get_seed()
        self.perlin_plant = PerlinNoise(settings.PLANT_SIZE)
        self.perlin_plant.SEED = get_seed() / 2
        self.game_time = game_time
        self.chunk_loaded = {}
        self.chunk_to_update = set()
        self.entity_to_update = set()
        self.canvas_owner = canvas_owner

    def load_surroundings(self, position : dict, author):

      self.perlin.SEED = get_seed()
      
      surroundings = (
          (0, 0), (-1, 0), (-1, 1), (0, 1),
          (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)
        )

      chunk_id = self.get_chunk_id(position)
      
      for pos in surroundings:
        chunk_load = (pos[0] + chunk_id[0], pos[1] + chunk_id[1])
        self.load_chunk(chunk_load ,author)

    def unload_surroundings(self, position : dict, author):
      surroundings = (
          (0, 0), (-1, 0), (-1, 1), (0, 1),
          (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)
        )

      chunk_id = self.get_chunk_id(position)
      
      for pos in surroundings:
        chunk_load = (pos[0] + chunk_id[0], pos[1] + chunk_id[1])
        self.unload_chunk(chunk_load ,author)

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

      # define which class to read from
      class_entity = {
        "seed" : sb.Seed
      }
      
      if "entity" in group:
        # entity
        block = class_entity[name_type](self.canvas_owner, char, position, name_type, name_type, self , groups=group)
      else:
        # regular block
        block = Block(self.canvas_owner, char, position, name_type, name_type, self, groups=group)

      chunk_id = self.get_chunk_id(position)
      self.chunk_to_update.add(chunk_id)

  
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

        # if chunk needs a save, save it before destroying it
        if chunk_id in self.chunk_to_update:
          self.save_chunk(chunk_id)
          self.chunk_to_update.remove(chunk_id)

        chunk_loaded_instance = self.chunk_loaded[chunk_id]["data"].copy()
        for b in chunk_loaded_instance:
            b.kill()

        del self.chunk_loaded[chunk_id]

      
    def read_chunk(self, path, position):

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
        world_noise = self.perlin.get_perlin_at(chunk_position)
        plant_noise = self.perlin_plant.get_perlin_at(chunk_position)
        new_block = Generation.define_block(world_noise, plant_noise , chunk_position)
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

                world_noise = self.perlin.get_perlin_at(pos_placement)
                plant_noise = self.perlin_plant.get_perlin_at(pos_placement)
                block_info = Generation.define_block(world_noise, plant_noise ,pos_placement)
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
        
        self.perlin.reset_gradient_cache()


    def reset_data(self):
      for f in os.listdir("Chunks"):
        os.remove(f"Chunks/{f}")
      for d in os.listdir("PlayerData"):
        os.remove(f"PlayerData/{d}")
      for f in os.listdir("LocalBlockData"):
        os.remove(f"LocalBlockData/{f}")

      
    def save_chunk(self, chunk_id):

      if not chunk_id in self.chunk_loaded:
        # prevent from saving an unloaded chunk
        # resulting in saving the chunk as being empty
        return
        
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
            if issubclass(block_save.__class__, Block):
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
                if issubclass(block_save.__class__, Block):
                  new_block = block_save.block_id
                  break
                else:
                  print(block_save.name, "Block Save Refused")
              

          block_counter += 1

      save_chunk += f"{block_counter + 1}{last_block}"
      
      
      file_chunk = open(f"Chunks/{chunk_id[0]},{chunk_id[1]}.txt", "w")
      file_chunk.write(save_chunk)
      file_chunk.close()
      

    def get_nearby_players(self, player, players):
      chunk_id = self.get_chunk_id(player.position)
      player_in_chunk = self.chunk_loaded[chunk_id]["players"].copy()

      nearby_players = set()
      players_to_check = players.copy()
      players_to_check.remove(player.name)
     
      for player_check in players_to_check:
        player_ref = self.canvas_owner.get_sprite(player_check)
        list_position_check = (player_ref.position["x"], player_ref.position["y"])
        list_position_player = (player.position["x"], player.position["y"])
        distance = math.dist(list_position_check, list_position_player)
        if distance <= MAX_DISTANCE_NEARBY:
          nearby_players.add(player_ref)
      
          
      return nearby_players

    def update_entity(self):
      entity_to_update_instance = self.entity_to_update.copy()
      updates = []
      for entity in entity_to_update_instance:
        output_position = entity.update()
        if not output_position is None:
          updates.append(output_position)
          
      return updates
      