from settings import *

previous_result = {}
SEED = get_seed()

class Generation:
  @staticmethod
  def define_block(value : float,
                   value_plant : float,
                   position : tuple):

      if value >= STONE[0] and value <= STONE[1]:
        return Generation.solid_block(value, position)
      else:
        # pass
        return Generation.air_block(value, value_plant, position)

  @staticmethod
  def air_block(value, value_plant, position):
    output = Generation.shop(value, position)
    if output is None:
      output = Generation.plant(value, value_plant, position)
    return output

  @staticmethod
  def plant(value, value_plant, position):
    if value_plant >= PLANT[0] and value_plant <= PLANT[1]:
      print(f"PLACE at {position}")
      return BLOCKS["plant_grown"]
      
  
  @staticmethod
  def solid_block(value : float, position : tuple):
    
    # so that result are reproductible
    seed = random.seed((position[0] + SEED, position[1] + SEED))
    # pick random key that is a probability of how likely will the ore spawn
    chose_ore = random.choice(list(ORES.keys()))
    probability = ORES[chose_ore]["proba"]
    neighboor_count = ORES[chose_ore]["max"]
    is_neighboor = False
        
    # check if has neighboor if yes then more prob to spawn one
    neighboor_positions = ( (1, 0), (0, 1), (-1, 0), (0, -1) )

    previous_result.setdefault(chose_ore, {})
    for x, y in neighboor_positions:
      pos_check = (position[0] + x, position[1] + y)
      if pos_check in previous_result[chose_ore]:
        neighboor_count = previous_result[chose_ore][pos_check] - 1
        if neighboor_count > 0:
          neighboor_proba = ORES[chose_ore]["neighboor"]
          probability += (1.0 - probability) * neighboor_proba
          is_neighboor = True
        break
        
    if random.random() <= probability:
      # ore placed
      # save in previous result
      previous_result[chose_ore][position] = neighboor_count
      return BLOCKS[chose_ore]
    else:
      # if no ore place a block
      return BLOCKS["stone"]
      


  @staticmethod
  def shop(value : float, position : tuple):
    if value >= SHOP["range"][0] and value <= SHOP["range"][1]:

      # possible place to generate
      random.seed((position[0] + SEED, position[1] + SEED))
      
      if random.random() <= SHOP["proba"]:
        # place it
        return BLOCKS["shop"]
    