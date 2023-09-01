import pickle
import os
from .player import Player
import random
from settings import PERLIN_SIZE, CANVAS_SIZE
from oz_engine import Camera

class PlayerLoader:
  @staticmethod
  def load_data(owner : str):
    data = open(f"PlayerData/{owner}.txt", "rb")
    data = pickle.load(data)
    print(data, "Loading Data")
    return data

  @staticmethod
  def create_data(owner : str):
    # define random position
    position = {
      "x" : random.randint(-3, 3) * PERLIN_SIZE[0],
      "y" : random.randint(-3, 3) * PERLIN_SIZE[1]
    }

    data = {"position" : position, "inventory": {}}
    # write data
    file = open(f"PlayerData/{owner}.txt", "wb")
    pickle.dump(data, file)
    file.close()
    # open data
    file = open(f"PlayerData/{owner}.txt", "rb")
    return pickle.load(file)
    
  @staticmethod
  def save_data(owner):
    data = {
      "position" : owner.position,
      "inventory" : owner.inventory
    }
    
    file = open(f"PlayerData/{owner.name}.txt", "wb")
    pickle.dump(data, file)
    file.close()
    
  @staticmethod
  def init_data(owner : str, canvas):
    
     
    if os.path.isfile(f"PlayerData/{owner}.txt"):
      # load data if something is already writen
      print("Load data")
      data = PlayerLoader.load_data(owner)
    else:
      print("Create data")
      data = PlayerLoader.create_data(owner)

    # get position from data file
    position = data["position"]
    inventory = data["inventory"]
    # create camera

    SIZE_X = CANVAS_SIZE[0]
    SIZE_Y = CANVAS_SIZE[1]
    
    camera = Camera(    canvas, {"x" : SIZE_X , "y" : SIZE_Y },
                           {"x" : -position["x"] + int(SIZE_X / 2),
                            "y" : -position["y"] + int(SIZE_Y / 2)}, 
                           f"camera_{owner}"
                     )
     
    # create player
    player = Player(canvas, "@", position, owner, camera, inventory, layer=2)
    # add reference / camera to returned data (not saved/writen)
    data["reference"] = player
    data["camera"] = camera
     
    return data
