import pandas as pd
from pprint import pprint
import json

df = pd.read_json('bot_agents.json')
pprint(df[['market_1', 'market_2', 'order_m1_size', 'order_m2_size']])

# open_positions_file = open("bot_agents.json")
# open_positions_dict = json.load(open_positions_file)

# pprint(open_positions_dict)