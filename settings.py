import os
import random


def get_seed():
  if os.path.isfile("Chunks/seed.txt"):
    SEED = float(open("Chunks/seed.txt", "r").read())
    return SEED
  else:
    SEED = random.random()
    seed_file = open("Chunks/seed.txt", "w")
    seed_file.write(str(SEED))
    seed_file.close()
    print("CREATE SEED")
    return SEED

PERLIN_SIZE = (30, 15)
PLANT_SIZE = (15, 15)
CANVAS_SIZE = (32, 13)

SERVER_ID = "Mineflat"
MAX_DISTANCE_NEARBY = 25.0


BLOCKS = {
  "stone": {"name": "stone", "char": "█", "group" :["wall"]},
  "iron": {"name": "iron" ,"char": "*", "group" : ["wall"]},
  "diamond" : {"name": "diamond" ,"char": "✦", "group" : ["wall"]},
  "coal" : {"name": "coal" ,"char": "#", "group" : ["wall"]},
  "shop" : {"name" : "shop", "char": "$", "group" : ["wall", "shop", "no-mine"]},
  "plant_grown" : {"name" : "plant_grown", "char" : "♣", "group": []}
}


ORES = {
  "iron" : {"proba" : 0.05, "neighboor" : 0.5, "max": 8, "price_unit" : 3},
  "diamond" : {"proba" : 0.0025, "neighboor" : 0.45, "max": 4, "price_unit" : 6},
  "coal" : {"proba" : 0.08, "neighboor" : 0.75, "max" : 10, "price_unit" : 1},
}

STONE = (0.0001, 1.0)
SHOP = {"range" : (-1 , -0.00001), "proba" : 0.001}
PLANT = (-1, -0.5)

AMOUNT_ARTICLE_RANGE = (1, 2)
DAY_CHANGE = 2