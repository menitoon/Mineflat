import discord
import Structures as st
import settings

NUMBERS = (
          ("1️⃣"), ("2️⃣"), ("3️⃣"), ("4️⃣"), ("5️⃣"), ("6️⃣"), ("7️⃣"), ("8️⃣"), ("9️⃣"), ("🔟")
        )

class GameCommands:

  __slot__ = "open_rooms"

  def __init__(self, open_rooms : dict):
    self.open_rooms = open_rooms
  
  async def shop(self, player, reaction):

    shop_position = player.is_shop_near()
    print(shop_position, "SHOP POSITION")
  
    if not shop_position is None:
      if not player.is_near_shop:
        # add reaction to enter shop
        await reaction.message.add_reaction("🛒")
        player.is_near_shop = True
      elif str(reaction) == "🛒":
        #execute shop
        player.is_in_shop = True
        # get channels, message, chat info
        channel = reaction.message.channel
        screen = self.open_rooms[channel]["screen"]
        chat = self.open_rooms[channel]["chat"]

        shop = st.Shop(shop_position)
        articles = shop.define_articles()
        text = "---Shop---\n"
        inventory = player.inventory.copy()
        print(inventory)
        for article in articles:
          char = settings.BLOCKS[article]["char"]
          char = "\*" if char == "*" else char
          sentence =  f"-{char} {article} : {articles[article]} coins"

          if article in inventory:
            # if object is in inventory
            sentence += f", you have {inventory[article]}"
            sentence = "**" + sentence + "**"
          else:
            # unable to buy
            sentence = "*" + sentence + "*"
          sentence += "\n"
          text += sentence
        
        # check if inventory is empty
        if inventory == {}:
          text += "..."
        
        shop_message = await chat.send(text)

        self.open_rooms[channel]["shop_message"] = shop_message
        self.open_rooms[channel]["shop_article"] = articles
        
        
        for emoji, article in zip(NUMBERS, articles):
          if article in inventory: 
            await shop_message.add_reaction(emoji)
            
        await shop_message.add_reaction("❌")
    else:
      player.is_in_shop = False


  async def handle_shop_transaction(reaction, channel):
  
    str_reaction = str(reaction)
    articles = self.open_rooms[channel]["shop_article"]
    chat = self.open_rooms[channel]["chat"]

    if str_reaction == "❌":
      # go back case
      pass
    
    for number, article in zip(NUMBERS, articles):
      if number == str_reaction:
        await chat.send(f"How many {article} do you want to sell ?")
        break
