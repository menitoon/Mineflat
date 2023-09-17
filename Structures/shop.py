import datetime
import random 
from settings import *

SEED = get_seed()

class Shop:
  __slot__ = "position"

  def __init__(self, position : dict):
    self.position = position


  def define_articles(self):

    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    current_day = int(current_date.day / DAY_CHANGE)
    
    
    seed = current_year + current_month + current_day + SEED
    # set random's seed
    random.seed(
      (seed + self.position["x"],
       seed + self.position["y"])
               )
    # pick amount of articles that are getting sold
    amount_of_articles = random.randint(AMOUNT_ARTICLE_RANGE[0], AMOUNT_ARTICLE_RANGE[1]) 
    articles = {}
    # things that can be sold
    articles_to_pick = ORES.copy()
    articles_to_pick = list(articles_to_pick.keys())

    article_base_unit = random.randint(2, 10)
    
    for article in range(amount_of_articles):
      article_chosen = random.choice(articles_to_pick)
      articles_to_pick.remove(article_chosen)
      ore_unit = ORES[article_chosen]["price_unit"]
      articles[article_chosen] = ore_unit * article_base_unit

    return articles


  def get_article_sentence(self, articles, player):
  
    text = "# Shop\n"
    inventory = player.inventory
    has_item = []
    index_place = 0
    
    for article in articles:
      char = BLOCKS[article]["char"]
      char = "\*" if char == "*" else char
      sentence =  f"-{char} {article} : {articles[article]} coins"

      if article in inventory:
        # if object is in inventory
        sentence += f", you have {inventory[article]}"
        sentence = "**" + sentence + "**"
        has_item.append({article : index_place})
      
      else:
        # unable to buy
        sentence = "*" + sentence + "*"
        
      index_place += 1
      sentence += "\n"
      text += sentence
        
    
    return {
      "text" : text,
      "has_item" : has_item
    }