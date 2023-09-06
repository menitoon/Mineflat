import datetime
import random 
from settings import DAY_CHANGE, ORES, AMOUNT_ARTICLE_RANGE, get_seed

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