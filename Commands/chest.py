from Structures import Chest

class Chest:

  __slot__ = "chest"
  
  def __init__(self, chest):
    self.chest = chest

  async def get_inventory(self, ctx):
    # get the inventory of the chest
    chat = ctx.channel
    chest = Chest()
    