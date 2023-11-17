from .chest_manager import *
from settings import CHEST_SLOTS, ITEMS, BLOCKS

# emojis
NUMBERS = (
  ("1️⃣"), ("2️⃣"), ("3️⃣"), ("4️⃣"), ("5️⃣"), ("6️⃣"), ("7️⃣"), ("8️⃣"), ("9️⃣"), ("🔟")
)

class BotManager:

  __slot__ = "chest", "open_rooms"
  
  def __init__(self, open_rooms):
    self.open_rooms = open_rooms


  async def send_inventory(self, channel, table_position):
    """ get the inventory of the chest """

    chest = ChestManager(table_position)
    
    inventory_string = "# Chest\n"
    for slot in chest.inventory:
      if slot is None:
        # empty slot
        inventory_string += "*- ...*"
      else:
        # item
        item, amount = list(slot.items())[0]
        icon = ""
        if item in BLOCKS:
          # item is a block
          icon = BLOCKS[item]["char"]
        else:
          # item is an item
          icon = ITEMS[item]["char"]
          
        inventory_string += f"**- {item} {icon} x{amount}**"
      inventory_string += "\n"
    
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
    
    chest = ChestManager(table_position)
    choice_slot = self.open_rooms[channel].get("choice_slot")
    if not choice_slot is None:
      # if choice is already chosen
      if str_reaction == "🤌":
        # take        
        if chest.inventory[choice_slot] is None:
          # if there is an empty slot 
          await chat.send("**⚠️Slot is empty, please select a proper slot !**")
          # reset slot choice
          del self.open_rooms[channel]["choice_slot"]
          # send back the message to select an other option
          message_chest_new = await self.send_inventory(channel, table_position)
          self.open_rooms[channel]["message_chest"] = message_chest_new
        else:
          await chat.send("How much do you want to take ?\n*use !take [amount]*")
      elif str_reaction == "✋":
        # drop stuff
        await chat.send("What do you want to drop and how much ?\n*use !drop [item] [amount]*")
    else:
      await self.choice_slot(reaction, chat, channel)
    
    await reaction.remove(user)

  
  async def choice_slot(self, reaction, chat, channel):
    if str(reaction) == "❌":

      player = self.open_rooms[channel]["player"]
      player.table = None
      player.is_in_table = False
      
      if not self.open_rooms[channel].get("choice_slot") is None:
        del self.open_rooms[channel]["choice_slot"]
      del self.open_rooms[channel]["table_position"]
    
    else:
      reaction_index = NUMBERS.index(str(reaction))
      self.open_rooms[channel]["choice_slot"] = reaction_index     
      table_position = self.open_rooms[channel]["table_position"]
      chest = ChestManager(table_position)
      if chest.inventory[reaction_index] is None:
        # can't select take since is empty
        action_message = await chat.send(f"What do you want to do with {str(reaction)}?\n**✋ = drop**\n*🤌 = take*")
      else:
        # all options are possible 
        action_message = await chat.send(f"What do you want to do with {str(reaction)}?\n**✋ = drop**\n**🤌 = take**")
        await action_message.add_reaction("🤌")

      
      # can always drop something so add reaction in any cases
      await action_message.add_reaction("✋")
      
