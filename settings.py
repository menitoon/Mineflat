import os
import random


def get_seed():
  if os.path.isfile("Chunks/seed.txt"):
    SEED = float(open("Chunks/seed.txt", "r").read())
    return SEED
  else:
    SEED = random.random()
    open("Chunks/seed.txt", "w").write(str(SEED))
    return SEED

PERLIN_SIZE = (30, 15)
CANVAS_SIZE = (32, 13)


BLOCKS = {
  "stone": {"name": "stone", "char": "█", "group" :["wall"]},
  "iron": {"name": "iron" ,"char": "*", "group" : ["wall"]},
  "diamond" : {"name": "diamond" ,"char": "✦", "group" : ["wall"]},
  "coal" : {"name": "coal" ,"char": "#", "group" : ["wall"]}
  
}

ORES = {
  "iron" : {"proba" : 0.05, "neighboor" : 0.4, "max": 8},
  "diamond" : {"proba" : 0.001, "neighboor" : 0.25, "max": 4},
  "coal" : {"proba" : 0.08, "neighboor" : 0.85, "max" : 10}
}

STONE = (0.0001, 1.0)