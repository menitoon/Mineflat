from .chest_manager import *
from settings import CHEST_SLOTS

# emojis
NUMBERS = (
  ("1️⃣"), ("2️⃣"), ("3️⃣"), ("4️⃣"), ("5️⃣"), ("6️⃣"), ("7️⃣"), ("8️⃣"), ("9️⃣"), ("🔟")
)

class BotManager:

  __slot__ = "chest", "open_rooms"
  
  def __init__(self, open_rooms):
    self.open_rooms = open_rooms


  async def send_inventory(self, reaction, table_position):
    """ get the inventory of the chest """

    chest = ChestManager(table_position)
    
    inventory_string = "# Chest\n"
    for slot in chest.inventory:
      if slot is None:
        # empty slot
        inventory_string += "- ..."
      else:
        # item
        item, amount = list(slot.items())[0]
        inventory_string = f"- {item} x{amount}"
      inventory_string += "\n"
    
    channel = reaction.message.channel
    chat = self.open_rooms[channel]["chat"]
    message_chest = await chat.send(inventory_string)
    
    
    for number_index in range(CHEST_SLOTS):
      number_reaction = NUMBERS[number_index]
      await message_chest.add_reaction(number_reaction)

    await message_chest.add_reaction("❌")
    
    self.open_rooms[channel]["message_chest"] = message_chest


  
  async def handle_chest_reaction(self, reaction, user, table_position):
    str_reaction = str(reaction)
    chat = reaction.message.channel
    channel = chat.parent
    message_chest = self.open_rooms[channel]["message_chest"]
    
    if not self.open_rooms[channel].get("choice") is None:
      # if choice is already chosen
      if str_reaction == "🤌":
        # take
        pass
      else:
        # drop stuff
        pass
    else:
      await self.choice(reaction, chat, channel)
    

    await reaction.remove(user)


  async def choice(self, reaction, chat, channel):
    if str(reaction) == "❌":
      self.player.table = None
      self.player.is_in_table = False

      if not self.open_rooms[channel].get("choice") is None:
        del self.open_rooms[channel]["choice"]

    else:
      self.open_rooms[channel]["choice"] = reaction
      await chat.send(f"What do you want to do with {str_reaction}?\n🤌 = take\n✋ = drop")
      await chat.add_reaction("🤌")
      await chat.add_reaction("✋")
      
