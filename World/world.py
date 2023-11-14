from . import Shop
from . import Chest

import datetime


class World:

  __slot__ = "bot", "open_rooms", "chunk_loader", "player_to_update", "players", "shop", "chest", "canvas", "player", "table_postion", "reaction"
  
  def __init__(self, bot,  canvas,  open_rooms, chunk_loader, player_to_update, players):
    
    self.bot = bot
    self.canvas = canvas
    self.open_rooms = open_rooms
    self.chunk_loader = chunk_loader
    self.player_to_update = player_to_update
    self.players = players
    
    self.shop = Shop.BotManager(open_rooms)
    self.chest = Chest.BotManager(open_rooms)
  
  async def act(self, reaction):
    channel = reaction.message.channel
    if str(channel) != "Chat":
      self.open_rooms[channel]["last_activity"] = datetime.datetime.utcnow()
    
    if str(channel) == "Chat":
      channel = channel.parent
    
    player = self.open_rooms[channel]["player"]
    camera = self.open_rooms[channel]["camera"]
    author = self.open_rooms[channel]["author"]
    self.reaction = reaction
    self.player = player 
    
    await reaction.remove(author)

    if not player.table is None:
      await self.act_table()
    else:
      # act screen
      await self.act_screen(author)
    
  async def act_screen(self, author):
    # position to update for rendering (where things move)
    player = self.player
    camera = player.camera
    position_to_update = []
    s_reaction = str(self.reaction)
    old_pos = self.player.position.copy()
    player.move(s_reaction)

    need_local_update = False
    need_table_update = False

    if s_reaction == "⛏️":
      position_mined = player.mine(self.chunk_loader, self.player_to_update)
      if not position_mined is None:
        position_to_update.append(position_mined)
        need_local_update = True
    
    elif s_reaction == "🔄":
      player.turn()
      need_local_update = True

    elif s_reaction == "🏗️":
      need_local_update = player.build(self.chunk_loader)
      print(need_local_update, "BUILD")
      if need_local_update == False:
        # execute build command and checks if 
        # was able to build if not 
        # return and end function
        return
      else:
        # if you built something add to update list
        direction = self.player.get_position_direction()
        position_selected = {
          "x" : direction["x"] + player.position["y"],
          "y" : direction["y"] + player.position["y"]
        }
        position_to_update.append(position_selected)
    
    
    in_common = self.is_in_table(old_pos, str(self.reaction))
    if in_common != set():
      # get first element(only element in set)
      in_common = list(in_common)[0]
      self.table_position = World.get_direction(str(self.reaction))

      TABLE_FUNCTION = {
        "shop" : self.init_shop,
        "chest" : self.init_chest
      }

      await TABLE_FUNCTION[in_common]()
    
    # player moved
    if old_pos != player.position:
      # add to player queue to update
      self.player_to_update.add(self.player)
      # add player's position to render queue
      position_to_update.append(player.position)
      need_local_update = True
      # self.chunk_loader updates itself
      self.chunk_loader.load_and_unload_chunks(old_pos, player.position, author)

    if not need_local_update:
      #No visual update needed, end function
      return
    else:
      await self.send_update(camera, player, self.reaction.message)
      if position_to_update != []:
        await self.update_screens(position_to_update, camera)
        
  def get_nearby_string(self, player):
    # get players nearby a specific player
    nearby_players = self.chunk_loader.get_nearby_players(player, self.players)
    nearby_str = ""

    # if there are players nearby
    if nearby_players != set():
      # add nearby info
      nearby_str = "nearby players:\n"
      for player_near in nearby_players:
        nearby_str += f"⬤ {player_near.name}\n"
    return nearby_str

  
  async def send_update(self, camera, player, message):

    r = camera.render()
    string_pos = f'({player.position["x"]}, {player.position["y"]})'
    nearby_info = self.get_nearby_string(player)
    
    message_content = f"```{r}\n{string_pos}\nDirection : {player.get_turn_str()}\n{nearby_info}```"

    await message.edit(
      content=message_content
    )

  
  async def update_screens(self, position_list : list, camera):
    # update for other screens
      for todo_camera in self.canvas.camera_tree:
        # if todo_camera is not the camera we are updating
        if todo_camera != camera:

          # check
          is_renderable = False
          for position in position_list:
            if todo_camera.is_renderable(position):
              is_renderable = True
              break
          # if one of these are renderable do an update
          # for the camera concerned
          if is_renderable:        
            camera_info = camera_room[todo_camera]
            player_updated = camera_info['owner']
            screen_x = player_updated.position["x"]
            screen_y = player_updated.position["y"]

            nearby_info = self.get_nearby_string()

            await camera_info["message"].edit(
              content=f"```{todo_camera.render()}\n({screen_x}, {screen_y})\nDirection : {player_updated.get_turn_str()}\n{nearby_info}```"
            )

  @staticmethod
  def get_direction(reaction : str):
    movement_dict = {
      "🔼" : {"x" : 0, "y" : -1},
      "🔽" : {"x" : 0, "y" : 1},
      "◀" : {"x" : -1, "y" : 0},
      "▶" : {"x" : 1, "y" : 0}
    }

    return movement_dict[reaction]


  async def act_table(self):
    table = self.player.table
    ACT_METHOD = {
      "shop" : self.act_shop,
      "chest" : self.act_chest
    }
    
    await ACT_METHOD[table]()
  
  def is_in_table(self, old_position, reaction : str):

    
    direction = World.get_direction(reaction)
    destination_pos = {"x" : direction["x"] + old_position["x"], "y" : direction["y"] + old_position["y"]}

    tables = {"shop", "chest"}
    
    for collision in self.canvas.get_elements(destination_pos):
      sprite_ref = self.canvas.get_sprite(collision)
      # check if list tables has some element in common with list sprite_ref.groups
      in_common = tables.intersection(sprite_ref.groups)
      return in_common

  async def init_shop(self):
    self.player.table = "shop"
    await self.shop.shop(self.player, self.reaction, self.table_position)

  async def act_shop(self):
    channel = self.reaction.message.channel.parent
    author = self.open_rooms[channel]["author"]
    await self.shop.handle_shop_transaction(self.reaction, author, channel)
  
  async def init_chest(self):
    self.player.table = "chest"
    channel = self.reaction.message.channel
    self.open_rooms[channel]["table_position"] = self.table_position
    await self.chest.send_inventory(channel, self.table_position)
  
  async def act_chest(self):
    channel = self.reaction.message.channel.parent
    author = self.open_rooms[channel]["author"]
    await self.chest.handle_chest_reaction(self.reaction, author, self.table_position)