import time

class GameTime():
  __slots__ = "time_in_game", "time_since"
  
  def __init__(self):
    self.init_time()
  
  def update_time(self):
    self.time_in_game = time.time() - self.time_since
  
  def init_time(self):
    self.time_since = time.time()
    self.time_in_game = 0
    