import discord 
from discord.ext import commands, tasks

import oz_engine as oz
import custom_class as cc
import Structures as st
import settings
import Commands as cd
from keep_alive import keep_alive

import random as rng
import math
import os
import time
import datetime
import random
import pickle
import time


keep_alive()
TOKEN = os.environ["TOKEN"] 
intents = discord.Intents.default()
intents.typing = True  
intents.presences = False
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.message_content = True

player_count = 0

bot = commands.Bot(command_prefix='!', intents=intents)

open_rooms = {}
camera_room = {}
players = set()


CATEGORY_ROOM = "Game-Rooms"
TIMEOUT_LIMIT = 300 # in seconds

SIZE_X = settings.CANVAS_SIZE[0]
SIZE_Y = settings.CANVAS_SIZE[1]

player_to_update = set()

canvas = oz.Canvas(" ")
cc.canvas = canvas
commands = cd.ShopCommands(open_rooms)
chunk_loader = cc.ChunkLoader(canvas, (SIZE_X, SIZE_Y), 5)
#chunk_loader.reset_data()


@bot.event
async def on_ready():

    global SERVER_NAME
    global GUILD
  
    print(f'Logged in as {bot.user.name}')
    print('------')
    update_check.start()
    check_inactivity.start()

    # delete all rooms at startup
    SERVER_NAME = settings.SERVER_ID
    GUILD = discord.utils.get(bot.guilds, name=SERVER_NAME) 
  
    # get category id
    GAME_ROOM_CAT = discord.utils.get(GUILD.categories, name=CATEGORY_ROOM) 

    # iterate through every channel and delete them
    await delete_all_channel_from_category(GAME_ROOM_CAT)

    # delete all token 
    roles = GUILD.roles
    for r in roles:
      if str(r).startswith("GAMETOKEN#"):
        await r.delete()
    
async def delete_all_channel_from_category(category):
    for channel in category.channels:
      await channel.delete()

@bot.command()
async def start(ctx):

    global player_count
  
    print("Command initiated !")
    str_author = str(ctx.author)
    
    if str_author in players:
      return
    print(str_author)
    players.add(str_author)
    print(players, "LIST")
    player_count += 1
    print(player_count, "ADD")
    role = await ctx.guild.create_role(name=f"GAMETOKEN#{player_count}")
    

    await ctx.send(f"Creating game room for {ctx.author.mention}, please wait a moment...")
    await ctx.author.add_roles(role)

    # define rules of private channel
    rules = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role: discord.PermissionOverwrite(read_messages=True, send_messages=False)
    }
    
    # get category id
    category = discord.utils.get(ctx.guild.categories, name=CATEGORY_ROOM)
    
    # Create the private channel with the specified name and permissions
    
    channel_name = f"Room#{player_count}"
    channel = await ctx.guild.create_text_channel(name=channel_name, overwrites=rules, category=category)

    is_new_player = not os.path.isfile(f"PlayerData/{str_author}.txt")
  
    # init player's data
    player_data = cc.PlayerLoader.init_data(str_author, canvas)
    player = player_data["reference"]
    player_pos = player_data["position"]
    camera = player_data["camera"]
  
    open_rooms[channel] = {
      "author" : ctx.author,
      "last_activity" : datetime.datetime.utcnow(),
      "player" : player,
      "camera" : camera
      }

    open_rooms[channel]["id"] = player_count
    chunk_loader.load_surroundings(player_pos, ctx.author)
    string_pos = f'({player.position["x"]},{player.position["y"]})'
  
    screen = await channel.send(f"```{camera.render()}\n{string_pos}\nDirection : {player.get_turn_str()}```")
    camera_room[camera] = {"message" : screen, "owner" : player}

    empty_message = await channel.send("‎")
    chat = await empty_message.create_thread(name="Chat", auto_archive_duration=60)
    # register additional keys
    open_rooms[channel]["chat"] = chat
    open_rooms[channel]["screen"] = screen

    if is_new_player:
      await chat.send(cd.help_message)
  
    # adds reactions to control
    await add_reactions(screen)

async def delete_roles_and_channel(channel):
  global player_count
  id_room = open_rooms[channel]["id"]
  role = discord.utils.get(GUILD.roles, name=f"GAMETOKEN#{id_room}")
  user = open_rooms[channel]["author"]
  
  await role.delete()
  del open_rooms[channel]
  await channel.delete()
  

@bot.command()
async def quit(ctx):
  global player_count

  if str(ctx.channel) != "Chat":
    return
    
  await close(ctx.channel.parent)

async def close(channel):
  global player_count
  player = open_rooms[channel]["player"]
  cc.PlayerLoader.save_data(player)
  author = open_rooms[channel]["author"]
  players.remove(player.name)
  print(players, "remove")
  # unload chunks that are loaded by no one
  
  chunk_loader.unload_surroundings(player.position, author)
  player.camera.kill()
  player.kill()

  await update_check()
  await delete_roles_and_channel(channel)
  if players == set():
    player_count = 0
    print(player_count, "RESET")
    
  
@tasks.loop(seconds=60)
async def check_inactivity():
  open_rooms_instance = open_rooms.copy()
  for channel in open_rooms_instance:
    async for message in channel.history(limit=1):
      time_since_message = datetime.datetime.utcnow() - open_rooms_instance[channel]["last_activity"]
      
      if time_since_message.total_seconds() >= TIMEOUT_LIMIT:
        await close(channel)
        
@tasks.loop(seconds=10)
async def update_check():
  global player_to_update
  
  for chunk in chunk_loader.chunk_to_update:
    chunk_loader.save_chunk(chunk)
    print(chunk, "TO UPDATE")
  chunk_loader.chunk_to_update = set()
  
  for player in player_to_update:
    # save player's data
    cc.PlayerLoader.save_data(player)
    print(player, "TO UPDATE")
  player_to_update = set()

@bot.command()
async def reset(ctx):
  if not ctx.author.guild_permissions.administrator:
    return
  chunk_loader.reset_data()
  await ctx.send("data got reset")

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
      
    channel = reaction.message.channel
    if str(channel) == "Chat":
      channel = channel.parent
    
    player = open_rooms[channel]["player"]

    if player.is_in_shop:
      await commands.handle_shop_transaction(reaction, user, channel)
    else:
      await act(reaction)

async def act(reaction):
    channel = reaction.message.channel
    if str(channel) != "Chat":
      open_rooms[channel]["last_activity"] = datetime.datetime.utcnow()
    player = open_rooms[channel]["player"]
    camera = open_rooms[channel]["camera"]
    author = open_rooms[channel]["author"]

    
    await reaction.remove(author)

    s_reaction = str(reaction)
    old_pos = player.position.copy()
    was_near = player.is_shop_near()
    player.move(s_reaction)

    need_update = False
  
    if s_reaction == "⛏️":
      player.mine(chunk_loader, player_to_update)
      need_update = True

    elif s_reaction == "🔄":
      player.turn()
      need_update = True
    
    elif s_reaction == "🏗️":
      need_update = player.build(chunk_loader)
      if need_update == False:
        # execute build command and checks if 
        # was able to build if not 
        # return and end function
        return

    await commands.shop(player, reaction)
    
    if old_pos != player.position:
      player_to_update.add(player)
      chunk_loader.load_and_unload_chunks(old_pos, player.position, author)
      if was_near and (not player.is_shop_near()):
        # if no longer near a shop remove that reaction
        screen = open_rooms[channel]["screen"]
        player.is_near_shop = False
        await screen.remove_reaction("🛒", bot.user)
        
      
    elif not need_update:
      #nothing todo
      return
    
    await send_update(camera, player, reaction.message)



async def send_update(camera, player, message):
  
  r = camera.render()
  string_pos = f'({player.position["x"]}, {player.position["y"]})'
  nearby_players = chunk_loader.get_nearby_players(player, players)

  nearby_str = ""
  
  if nearby_players != set():
    nearby_str = "nearby players:\n"
    for player_near in nearby_players:
      nearby_str += f"⬤ {player_near.name}\n"

  message_content = f"```{r}\n{string_pos}\nDirection : {player.get_turn_str()}\n{nearby_str}```"
  
  await message.edit(
    content=message_content
  )
  await update_screens(player, camera)
  

async def update_screens(player, camera):
  # update for other screens
    for todo_camera in canvas.camera_tree:
      if todo_camera != camera:
        if todo_camera.is_renderable(player.position):
          camera_info = camera_room[todo_camera]
          player_updated = camera_info['owner']
          screen_x = player_updated.position["x"]
          screen_y = player_updated.position["y"]

          nearby_str = ""
          nearby_players = chunk_loader.get_nearby_players(player_updated, players)
          
          if nearby_players != set():
            nearby_str = "nearby players:\n"
            for player_near in nearby_players:
              nearby_str += f"⬤ {player_near.name}\n"
          
          await camera_info["message"].edit(
            content=f"```{todo_camera.render()}\n({screen_x}, {screen_y})\nDirection : {player.get_turn_str()}\n{nearby_str}```"
          )


async def add_reactions(message):
  CONTROLS = ("◀", "🔽", "🔼", "▶", "⛏️", "🏗️" , "🔄",)
  for emoji in CONTROLS:
    await message.add_reaction(emoji)


@bot.command()
async def sell(ctx, amount):
  if str(ctx.channel) != "Chat":
    return
  await commands.sell(ctx, amount, player_to_update)

@bot.command()
async def coin(ctx):
  chat = ctx.channel
  if str(chat) != "Chat":
    return
  channel = chat.parent
  await commands.show_coin(channel)

@bot.command()
async def leader(ctx):
  await commands.leaderboard(ctx, players, canvas)

@bot.command()
async def inventory(ctx):
  chat = ctx.channel
  if str(chat) != "Chat":
    return
  channel = chat.parent
  player = open_rooms[channel]["player"]
  await chat.send(cd.PlayerCommands.show_inventory(player))
  
@bot.command()
async def change(ctx, block):
  chat = ctx.channel
  if str(chat) != "Chat":
    return

  channel = chat.parent
  player = open_rooms[channel]["player"]
  
  await chat.send(cd.PlayerCommands.change_block_type(player, block))

@bot.command()
async def tp(ctx, x, y):
  chat = ctx.channel
  if str(chat) != "Chat" or not ctx.author.guild_permissions.administrator:
    return

  channel = chat.parent
  author = open_rooms[channel]["author"]
  player = open_rooms[channel]["player"]

  cd.AdminCommands.tp(x, y, chunk_loader, author, player)
  
  screen = open_rooms[channel]["screen"]
  await send_update(player.camera, player, screen)

@bot.command()
async def give(ctx, item , amount):
  chat = ctx.channel
  if str(chat) != "Chat" or not ctx.author.guild_permissions.administrator:
    return

  channel = chat.parent
  player = open_rooms[channel]["player"]
  
  if cd.AdminCommands.give(item, amount, player):
    await chat.send(f"succesfully gave {amount} {item} to {player.name}")
  else:
    await chat.send(f"operation failed")


@bot.command()
async def clean(ctx):
  chat = ctx.channel
  if str(chat) != "Chat":
    return
  channel = chat.parent
  player = open_rooms[channel]["player"]
  player.inventory = {}
  player.coin = 0
  await chat.send("Inventory cleaned")

@bot.command()
async def get_help(ctx):
  if str(ctx.channel) != "Chat":
    return
  await ctx.channel.send(cd.help_message)

bot.run(TOKEN)