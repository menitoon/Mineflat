from .shop import *
import datetime

class World:

  __slot__ = "open_rooms", "chunk_loader", "player_to_update", "players", "shop", "canvas"
  
  def __init__(self, canvas,  open_rooms, chunk_loader, player_to_update, players):
    self.canvas = canvas
    self.open_rooms = open_rooms
    self.chunk_loader = chunk_loader
    self.player_to_update = player_to_update
    self.players = players
    self.shop = Shop(open_rooms)
  
  
  async def act(self, reaction):
    channel = reaction.message.channel
    if str(channel) != "Chat":
      self.open_rooms[channel]["last_activity"] = datetime.datetime.utcnow()
    player = self.open_rooms[channel]["player"]
    camera = self.open_rooms[channel]["camera"]
    author = self.open_rooms[channel]["author"]

    await reaction.remove(author)

    # position to update for rendering (where things move)
    position_to_update = []
    s_reaction = str(reaction)
    old_pos = player.position.copy()
    was_near = player.is_shop_near()
    player.move(s_reaction)
    
    need_local_update = False

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
      if need_local_update == False:
        # execute build command and checks if 
        # was able to build if not 
        # return and end function
        return
      else:
        # if you built something add to update list
        position_to_update.append(player.get_position_direction())

    await self.shop.shop(player, reaction)

    # player moved
    if old_pos != player.position:
      # add to player queue to update
      self.player_to_update.add(player)
      # add player's position to render queue
      position_to_update.append(player.position)
      need_local_update = True
      # self.chunk_loader updates itself
      self.chunk_loader.load_and_unload_chunks(old_pos, player.position, author)
      # if no longer near a shop remove that reaction
      if was_near and (not player.is_shop_near()):
        screen = self.open_rooms[channel]["screen"]
        player.is_near_shop = False
        await screen.remove_reaction("🛒", bot.user)

    if not need_local_update:
      #No visual update needed, end function
      return
    else:
      await self.send_update(camera, player, reaction.message)
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

  @staticmethod
  async def update_screens(position_list : list, camera):
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