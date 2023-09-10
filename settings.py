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
  "coal" : {"name": "coal" ,"char": "#", "group" : ["wall"]},
  "shop" : {"name" : "shop", "char": "$", "group" : ["wall", "shop", "no-mine"]}
  
}

ORES = {
  "iron" : {"proba" : 0.05, "neighboor" : 0.5, "max": 8, "price_unit" : 3},
  "diamond" : {"proba" : 0.001, "neighboor" : 0.25, "max": 4, "price_unit" : 6},
  "coal" : {"proba" : 0.08, "neighboor" : 0.85, "max" : 10, "price_unit" : 1}
}

STONE = (0.0001, 1.0)
SHOP = {"range" : (-1 , -0.00001), "proba" : 0.001}


AMOUNT_ARTICLE_RANGE = (1, 2)
DAY_CHANGE = 2