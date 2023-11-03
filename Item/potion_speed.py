
AMOUNT = 2
DURATION = 50

class PotionSpeed():
  
  @staticmethod
  def use(player):
    # give speed effect to player
    player.move_unit = AMOUNT
    player.effect["speed"] = DURATION