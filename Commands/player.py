from settings import BLOCKS, ITEMS
from World import Chest

help_message = """
# Welcome to Mineflat !

## Instructions

It seems like it's your first time playing it
so here are some instructions on how to play:
-Use ◀, 🔽, 🔼, ▶ to **move**
-Use ⛏️ to **mine**
-Use 🔄 to **change** your **direction** in which
 you are **mining and building**

## Gettings Coins

In order to get coins you have to mine ores
like Iron *, Diamond ✦ and Coal #.
Once you've done that go to a **Shop** represented by a "$"
and use "🛒" to access the shop 
In if you have any of those **ores** select the right reaction 
to select the one you want to sell then use "!sell [amount]" to sell your ores.
To escape the shop use "❌"
**NOTE :** 
**-in shop you won't be able to move or mine**
**-shop's articles will change every 2 day**


## Commands

**!quit** : quit your current session
**!coins** : to show the amount of coins you have
**!leader** : to show the leaderboard
**!inventory** : to show what's in your inventory
**!get_help** : to show the help instruction
**!change** *[block_type]* : to change the block you are using to build
"""


class PlayerCommands:

  @staticmethod
  def change_block_type(player, block):
    if block in player.inventory:
      player.block_in_hand = block
      return "Block in hand succesfully changed."
    else:
      return "Block isn't in your inventory."


  @staticmethod
  def show_inventory(player):
    inventory = player.inventory
    text = "# Inventory\n"
    
    for item, amount in inventory.items():

      char = ""
      if item in ITEMS:
        char = ITEMS[item]["char"]
      else:
        char = BLOCKS[item]["char"]
      
      text += f"🞄 {item} {char} : {amount}\n"

    if inventory == {}:
      text += "**-empty**"

    return text

  @staticmethod
  def use_item(player, item):
    if not item in player.inventory:
      return "You don't have this item in your inventory."
    else:
      ITEMS[item]["class"].use(player)
      return f"```{item} was succefully used```."

  @staticmethod
  def drop_item(item, amount, open_rooms, chat):
    channel = chat.parent

    amount = int(amount)
    player = open_rooms[channel]["player"]
    table_position = open_rooms[channel]["table_position"]

    if item in player.inventory:
      # item is in inventory
      # check if enough item of that type:
      if player.inventory[item] - amount >= 0:
        # enough item
        player.inventory[item] -= amount
      else:
        # amount desired is too important bruh
        return f"**️You don't have enough {item} to drop, you only have {amount} {item}.**"
    else:
      # player doesn't have this item in his inventory
      return f"**You don't have {item} in your inventory.**"
    chest = Chest.ChestManager(table_position)
    choice_slot = open_rooms[channel]["choice_slot"]
    sentence = chest.add_item(choice_slot, item, amount)
    return sentence

  @staticmethod
  def take_item(amount, open_rooms, chat):
    channel = chat.parent
    amount = int(amount)
    player = open_rooms[channel]["player"]
    table_position = open_rooms[channel]["table_position"]

    chest = Chest.ChestManager(table_position)
    choice_slot = open_rooms[channel]["choice_slot"]
    sentence = chest.remove_item(choice_slot, amount)
    return sentence