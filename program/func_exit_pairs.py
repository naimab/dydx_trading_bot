from constants import CLOSE_AT_ZSCORE_CROSS, MODE
from func_utils import format_number
from func_public import get_candles_recent
from func_cointegration import calculate_zscore
from func_private import check_order_status, close_order
import json
import time

# Manage trade exits
def manage_trade_exits(client):

    """
        Manage exiting open positions
        Based upon criteria set in constants
    """

    # Opening JSON file
    try:
        with open("bot_agents.json", 'r') as open_positions_file:
            open_positions_dict = json.load(open_positions_file)
    except Exception as e:
        print(f"Error opening or reading bot_agents.json: {e}")
        return "complete"
    
    # Guard: Exit if no open position in file
    if len(open_positions_dict) < 1:
        return "complete"
    
    # Get all open positions per trading platform
    exchange_pos = client.private.get_positions(status="OPEN")
    all_exc_pos = exchange_pos.data["positions"]
    
    # Prepare for modifications directly in the list
    updated_positions = []

    for position in open_positions_dict:

        # Protect API
        time.sleep(0.5)

        is_close = False
        # Extract position matching information from file - market 1
        position_market_m1 = position["market_1"]
        position_size_m1 = position["order_m1_size"]
        position_side_m1 = position["order_m1_side"]

        # Extract position matching information from file - market 2
        position_market_m2 = position["market_2"]
        position_size_m2 = position["order_m2_size"]
        position_side_m2 = position["order_m2_side"]

        # Get Prices
        try:
            series_1 = get_candles_recent(client, position_market_m1)
            time.sleep(0.2)
            series_2 = get_candles_recent(client, position_market_m2)
            time.sleep(0.2)
        except Exception as e:
            print(f"Error getting candles: {e}")  

        # Get markets for referece of tick size   
        try:
            markets = client.public.get_markets().data
            if markets is None:
                raise ValueError("Invalid get_markets response")
    
        except Exception as e:
            print(f"Encountered an error: {e}")
            return None
        
        time.sleep(0.2)

        # Triger close base on Z-Score
        if CLOSE_AT_ZSCORE_CROSS:

            # Initialize z_scores
            hedge_ratio = position["hedge_ratio"]
            intercept = position["intercept"]
            z_score_traded = position["z_score"]
            if len(series_1) > 0 and len(series_1) == len(series_2):
                spread = series_1 - (hedge_ratio * series_2 + intercept)
                z_score_current = calculate_zscore(spread).values.tolist()[-1]

            # Determine trigger
            z_score_level_check = abs(z_score_current) >= abs(z_score_traded)
            z_score_cross_check = (z_score_current < 0 and z_score_traded > 0) or (z_score_current > 0 and z_score_traded < 0)

            # Close trade
            if z_score_level_check and z_score_cross_check:
                # initiat close trigger
                is_close = True

            ###
            # Add any other close logic you want here
            ###

        # Close positions if triggerd
        if MODE == "DEVELOPMENT":
        # if is_close:

            # Determine side of m1
            side_m1 = "SELL" 
            if position_side_m1 == "SELL":
                side_m1 = "BUY"

            # Determine side of m2
            side_m2 = "SELL" 
            if position_side_m2 == "SELL":
                side_m2 = "BUY"

            # Get and format Price
            price_m1 = float(series_1[-1])
            price_m2 = float(series_2[-1])
            accept_price_m1 = price_m1 * 1.05 if side_m1 == "BUY" else price_m1 * 0.95
            accept_price_m2 = price_m2 * 1.05 if side_m2 == "BUY" else price_m2 * 0.95
            tick_size_m1 = markets["markets"][position_market_m1]["tickSize"]
            tick_size_m2 = markets["markets"][position_market_m2]["tickSize"]
            accept_price_m1 = format_number(accept_price_m1, tick_size_m1)
            accept_price_m2 = format_number(accept_price_m2, tick_size_m2)

            # Close positions
            try:

                # Close position for market 1
                print(">>> Closing market 1 <<<")
                print(f"Closing position for {position_market_m1}")
                print(f"Side: {side_m1}")

                close_order_m1 = close_order(
                  client,
                  market=position_market_m1,
                  side=side_m1,
                  size=position_size_m1,
                  price=accept_price_m1,
                )            

                # Protect API
                time.sleep(2)

                # Close position for market 2
                print(">>> Closing market 2 <<<")
                print(f"Closing position for {position_market_m2}")
                print(f"Side: {side_m2}")

                close_order_m2 = close_order(
                  client,
                  market=position_market_m2,
                  side=side_m2,
                  size=position_size_m2,
                  price=accept_price_m2,
                )

                time.sleep(2)
                # After placing close order, check if it was successful:
                close_status_m1 = check_order_status(client, close_order_m1["order"]["id"])
                close_status_m2 = check_order_status(client, close_order_m2["order"]["id"])

                if close_status_m1 == "FILLED":
                    print(f"Confirming closed position for {position_market_m1}")
                else:
                    print(f"Failed to close positions for {position_market_m1}")
                    updated_positions.append(position)  # Only append if the close failed

                if close_status_m2 == "FILLED":
                    print(f"Confirming closed for {position_market_m2}")
                else:
                    print(f"Failed to close positions for {position_market_m2}")
                    updated_positions.append(position)  # Only append if the close failed

            except Exception as e:
                print(f"Exit failed for pair: {position_market_m1} and {position_market_m2}") 
                updated_positions.append(position)
                # check if one is open and the other is not and if so close that position.

        #   Keep record of items and save
        else:
          updated_positions.append(position)

    # Save remaining items
    print(f"{len(updated_positions)} Items remaining. Saving file...")
    with open("bot_agents.json", "w") as f:
      json.dump(updated_positions, f)
