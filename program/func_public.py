from constants import RESOLUTION
from func_utils import get_ISO_times
from pprint import pprint
import numpy as np
import pandas as pd
import time

# Get relevant time periods for ISO from and to
ISO_TIMES = get_ISO_times()

pprint(ISO_TIMES)

# Construct market prices
def construct_market_prices(client):
    pass