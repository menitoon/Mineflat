import discord
import Structures as st
import settings
import custom_class as cc
import os

NUMBERS = (
          ("1️⃣"), ("2️⃣"), ("3️⃣"), ("4️⃣"), ("5️⃣"), ("6️⃣"), ("7️⃣"), ("8️⃣"), ("9️⃣"), ("🔟")
        )

class ShopCommands:

  __slot__ = "open_rooms"

  def __init__(self, open_rooms : dict):
    self.open_rooms = open_rooms
  
  async def shop(self, player, reaction):

    shop_position = player.is_shop_near()
    
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

        shop_info = shop.get_article_sentence(articles, player)
        text = shop_info["text"]
        has_item = shop_info["has_item"]
        
        shop_message = await chat.send(text)
        
        self.open_rooms[channel]["shop_message"] = shop_message
        self.open_rooms[channel]["shop_article"] = articles
        self.open_rooms[channel]["shop"] = shop
        inventory = player.inventory

        
        
        for article in has_item:

          key = list(article.values())[0]
          await shop_message.add_reaction(NUMBERS[key])
            
        await shop_message.add_reaction("❌")
    else:
      player.is_in_shop = False

 
  async def handle_shop_transaction(self, reaction, user, channel):
  
    str_reaction = str(reaction)
    articles = self.open_rooms[channel]["shop_article"]
    chat = self.open_rooms[channel]["chat"]

    if str_reaction == "❌":
      # go back case
      await reaction.remove(user)
      self.close(channel)
      player = self.open_rooms[channel]["player"]
      player.is_in_shop = False
      await reaction.message.delete()
      return
    
    for number, article in zip(NUMBERS, articles):
      if number == str_reaction:
        await chat.send(f"How many {article} do you want to sell ?")
        self.open_rooms[channel]["article_selected"] = article
        await reaction.remove(user)
        break

  async def sell(self, ctx, amount):

    chat = ctx.channel
    channel = chat.parent
    player = self.open_rooms[channel]["player"]
    type = self.open_rooms[channel].get("article_selected")
    shop = self.open_rooms[channel]["shop"]
    articles = self.open_rooms[channel]["shop_article"]
    
    if type is None:
      await chat.send("⚠️ Please select a proper article to sell !")
      return

    amount = int(amount)
    text = ""
    
    if not amount <= player.inventory[type]:
      # can't buy
      text += f"You can't sell {amount} please select a valid amount\n"
    else:
      # if can buy
      player.inventory[type] -= amount
      player.coin += articles[type]
      if player.inventory[type] == 0:
        del player.inventory[type]
      
    
    shop_info = shop.get_article_sentence(articles, player)
    text += shop_info["text"]
    has_item = shop_info["has_item"]
    
    shop_message = await chat.send(text)  
    self.open_rooms[channel]["shop_message"] = shop_message
    
    for article in has_item:
        key = list(article.values())[0]
        await shop_message.add_reaction(NUMBERS[key])
    await shop_message.add_reaction("❌")
    del self.open_rooms[channel]["article_selected"]

  def close(self, channel):
    del self.open_rooms[channel]["shop"]
    self.open_rooms[channel].pop("article_selected", None)
    del self.open_rooms[channel]["shop_article"]


  async def show_coin(self, channel):
    chat = self.open_rooms[channel]["chat"]
    player = self.open_rooms[channel]["player"]
    if player.coin > 1:
      await chat.send(f"You have {player.coin} coin 🪙")
    else:
      await chat.send(f"You have {player.coin} coins 🪙")


  async def leaderboard(self, ctx):

    chat = ctx.channel
    if str(chat) != "Chat":
      print(str(chat), "OOF")
      return
    
    leader = {}
    
    for player_file in os.listdir("PlayerData"):
      len_file = len(player_file)
      player_name = player_file[0 : len_file - 4]
      coin = cc.PlayerLoader.load_data(player_name)["coin"]
      leader[player_name] = coin
      
    
    leader =  sorted( leader.items(), key=lambda item : item[1], reverse=True)

    text = "---Leaderboard--\n"
    place = 1
    for player_name, coin in leader:
      text += f"**#{place} {player_name} : {coin}🪙**\n"
      place += 1

    await chat.send(text)

      