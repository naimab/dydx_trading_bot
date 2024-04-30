from func_utils import format_number
import json
import time
from pprint import pprint


def verify_json_positions(client):
    open_positions_file = open("bot_agents.json")
    open_positions_dict = json.load(open_positions_file)

    if not open_positions_dict:
        print("No open positions in file")
        return True
    
    else:
        exchange_pos = client.private.get_positions(status="OPEN")
        all_exc_pos = exchange_pos.data["positions"]

        markets_live = []
        for p in all_exc_pos:
            markets_live.append(p["market"])

            # Check all saved positions match order record
        # Exit trade according to any exit trade rules
        for position in open_positions_dict:

            # Extract position matching information from file - market 1
            position_market_m1 = position["market_1"]
            position_size_m1 = position["order_m1_size"]
            position_side_m1 = position["order_m1_side"]

            # Extract position matching information from fiel - market 2
            position_market_m2 = position["market_2"]
            position_size_m2 = position["order_m2_size"]
            position_side_m2 = position["order_m2_side"]

            # protect api
            time.sleep(0.5)

            # Get order info m1 per exchange
            try:
                order_m1 = client.private.get_order_by_id(position["order_id_m1"])
                if order_m1 is None:
                    raise ValueError

            except Exception as e:
                print(f"Network Error getting order_m1 by id: {e}")

            order_market_m1 = order_m1.data["order"]["market"]
            order_size_m1 = order_m1.data["order"]["size"]
            order_side_m1 = order_m1.data["order"]["side"]

            # protect api
            time.sleep(0.5)

            # Get order info m2 per exchange
            try:
                order_m2 = client.private.get_order_by_id(position["order_id_m2"])
                if order_m2 is None:
                    raise ValueError

            except Exception as e:
                print(f"Network Error getting order_m2 by id: {e}")

            order_market_m2 = order_m2.data["order"]["market"]
            order_size_m2 = order_m2.data["order"]["size"]
            order_side_m2 = order_m2.data["order"]["side"]

            # Perform matching checks
            check_m1 = (position_market_m1 == order_market_m1) and (position_size_m1 == order_size_m1) and (position_side_m1 == order_side_m1)
            check_m2 = (position_market_m2 == order_market_m2) and (position_size_m2 == order_size_m2) and (position_side_m2 == order_side_m2) 
            check_live = (position_market_m1 in markets_live) and (position_market_m2 in markets_live)
           
            if not check_m1 or not check_m2 or not check_live:
                print(f"Warning: Not all open position match exchange records for {position_market_m1} and {position_market_m2}")
                return False
            else:
                continue

        return True
        