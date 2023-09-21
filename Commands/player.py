from settings import BLOCKS

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
      text += f"🞄 {item} {BLOCKS[item]['char']} : {amount}\n"

    if inventory == {}:
      text += "**-empty**"

    return text

