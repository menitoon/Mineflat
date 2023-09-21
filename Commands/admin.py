from settings import BLOCKS, CANVAS_SIZE

class AdminCommands:
  
  @staticmethod
  def tp(x, y, chunk_loader, author, player):
    chunk_loader.unload_surroundings(player.position, author)

    x = int(x)
    y = int(y)
  
    player.set_position({"x" : x, "y" : y})
    chunk_loader.load_surroundings(player.position, author)
    camera = player.camera
    camera.set_position({"x" : x - int(CANVAS_SIZE[0] / 2), "y" : y - int(CANVAS_SIZE[1] / 2)})


  @staticmethod
  def give(item, amount, player):

    if not item in BLOCKS:
      return False

    amount = int(amount)
    does_exist = player.inventory.get(item)
    if does_exist is None:
      player.inventory[item] = amount
    else:
      player.inventory[item] += amount
      
    return True

  @staticmethod
  def clip(player):
    player.clip = not player.clip
    if player.clip:
      # if can clip
      # so set on
      return '```Clip proprety set to True```'
    else:
      # if can't clip
      # so set off
      return '```Clip proprety set to False```'


  @staticmethod
  def set_move_unit(player, unit : int):
    player.move_unit = unit
    return f"```{player.name}'s move unit set to {unit}```"