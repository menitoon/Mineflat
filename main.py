import discord 
from discord.ext import commands, tasks

import oz_engine as oz
import custom_class as cc
import settings
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
chunk_loader = cc.ChunkLoader(canvas, (SIZE_X, SIZE_Y), 5)
chunk_loader.reset_data()


@bot.event
async def on_ready():

    global SERVER_NAME
    global GUILD
  
    print(f'Logged in as {bot.user.name}')
    print('------')
    update_check.start()
    check_inactivity.start()

    # delete all rooms at startup
    SERVER_NAME = open("ID_SERVER.txt", "r").read()
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
    print("Command initiated !")
    str_author = str(ctx.author)
    
    if str_author in players:
      return
  
    players.add(str_author)
    role = await ctx.guild.create_role(name=f"GAMETOKEN#{len(open_rooms)}")
    

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
    channel_name = f"Room#{len(open_rooms)}"
    channel = await ctx.guild.create_text_channel(name=channel_name, overwrites=rules, category=category)
    
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

    
    chunk_loader.load_surroundings(player_pos, ctx.author)
    string_pos = f'({player.position["x"]},{player.position["y"]})'
  
    screen = await channel.send(f"```{open_rooms[channel]['camera'].render()}\n{string_pos}\nDirection : {player.get_turn_str()}```")
    camera_room[camera] = {"message" : screen, "owner" : player}

    empty_message = await channel.send("‎")
    chat = await empty_message.create_thread(name="Chat", auto_archive_duration=60)
    open_rooms[channel]["chat"] = chat
      
    # adds reactions to control
    CONTROLS = ("◀", "🔽", "🔼", "▶", "⛏️", "🏗️" , "🔄",)

    for control in CONTROLS:
      await screen.add_reaction(control)

async def delete_roles_and_channel(channel):
  room_id = list(open_rooms.keys()).index(channel) # get which "#" room (ex : 1, 2, 3 ect) 
  role = discord.utils.get(GUILD.roles, name=f"GAMETOKEN#{room_id}")
  user = open_rooms[channel]["author"]
        
  await role.delete()
  del open_rooms[channel]
  await channel.delete()

@bot.command()
async def quit(ctx):
  print(ctx.channel)
  if str(ctx.channel) != "Chat":
    return
  
  await close(ctx.channel.parent)

async def close(channel):
  player = open_rooms[channel]["player"]
  player.kill()
  author = open_rooms[channel]["author"]
  players.remove(str(author))

  # unload chunks that are loaded by no one
  for chunk_id in chunk_loader.chunk_loaded:

    chunk = chunk_loader.chunk_loaded[chunk_id]
    if chunk["players"] == set():
      chunk_loader.unload_chunk(chunk_id)

  await update_check()
  await delete_roles_and_channel(channel)
  
@tasks.loop(seconds=30)
async def check_inactivity():
  open_rooms_instance = open_rooms.copy()
  for channel in open_rooms_instance:
    async for message in channel.history(limit=1):
      time_since_message = datetime.datetime.utcnow() - open_rooms_instance[channel]["last_activity"]
      
      if time_since_message.total_seconds() >= TIMEOUT_LIMIT:
        await close(channel)
        
@tasks.loop(seconds=10)
async def update_check():
  for chunk in chunk_loader.chunk_to_update:
    chunk_loader.save_chunk(chunk)
    
  for player in player_to_update:
    # save position
    cc.PlayerLoader.save_data(player)

@bot.command()
async def reset(ctx):
  chunk_loader.reset_data()
  await ctx.send("data got reseted")

@bot.event
async def on_reaction_add(reaction, user):

    if user.bot:
        return
    
    await act(reaction, user)

async def act(reaction, user):
    channel = reaction.message.channel
    open_rooms[channel]["last_activity"] = datetime.datetime.utcnow()
    player = open_rooms[channel]["player"]
    camera = open_rooms[channel]["camera"]
    author = open_rooms[channel]["author"]
    
    await reaction.remove(author)

    s_reaction = str(reaction)
    old_pos = player.position.copy()

    
    player.move(s_reaction)
    
    if s_reaction == "⛏️":
      mine(player)

    elif s_reaction == "🔄":
      player.turn()
    
    elif s_reaction == "🏗️":
      if build(player) is False:
        # execute build command and checks if 
        # was able to build if not 
        # return and end function
        return
  
    elif old_pos != player.position:
      player_to_update.add(player)
    else:
      #nothing todo
      return
    
    
    chunk_loader.load_and_unload_chunks(old_pos, player.position, author)
  
    
    r = camera.render()
    string_pos = f'({player.position["x"]},{player.position["y"]})'
  
    await reaction.message.edit(
      content=f"```{r}\n{string_pos}\nDirection : {player.get_turn_str()}```"
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
          
          await camera_info["message"].edit(
            f"```{todo_camera.render()}\n({screen_x}, {screen_y})\nDirection : {player.get_turn_str()}```")
          
def mine(player):
  block_selected = ""
  block_pos = player.position.copy()
  reach_left = player.reach
  
  while (reach_left > 0) and (len(block_selected) < 1):
    block_pos["x"] += player.direction["x"]
    block_pos["y"] += player.direction["y"]
    block_selected = canvas.get_elements(block_pos)
    reach_left -= 1
    

  if len(block_selected) == 0:
    return
  
  chunk_id = chunk_loader.get_chunk_id(block_pos)
  chunk_loader.chunk_to_update.add(chunk_id)
  block_selected = canvas.get_sprite(block_selected[0])
  player_to_update.add(player)
  block_type = block_selected.block_id
  chunk_loader.chunk_loaded[chunk_id]["data"].remove(block_selected)
  block_selected.kill()
  player.inventory[block_type] = player.inventory.get(block_type, 0) + 1
  
def build(player):
  build_destination = {
    "x": player.position["x"] + player.direction["x"],
    "y": player.position["y"] + player.direction["y"]
                      }
  
  block_destination = canvas.get_elements(build_destination)
  
  if block_destination != []:
    # if there is a block return
    return False

  
  chunk_id = chunk_loader.get_chunk_id(build_destination)
  block = cc.Block(canvas, "█", build_destination, "stone", "stone")
  chunk_loader.chunk_loaded[chunk_id]["data"].add(block)
  return True
  
bot.run(TOKEN)