from constants import ZSCORE_THRESH, USD_PER_TRADE, USD_MIN_COLLATERAL
from func_utils import format_number
from func_public import get_candles_recent
from func_cointegration import calculate_zscore
from func_private import is_open_positions
from func_bot_agent import BotAgent
import pandas as pd
import json
from pprint import pprint



# Open Positions
def open_positions(client):

    """
        Manage finding triggers for trade entry 
        Store trades for managing later on exit function
    
    """

    # Load cointegrated pairs
    df = pd.read_csv("cointegrated_pairs.csv")

    # Get markets for referencing of min order size, tick size etc
    try:
        markets = client.public.get_markets().data
        if markets is None:
            raise ValueError("Invalid get_markets response")

    except Exception as e:
        print(f"Encourntered an error: {e}")
        return None



    # Opening JSON file
    try:
        open_positions_file = open("bot_agents.json")
        open_positions_dict = json.load(open_positions_file)

        bot_agents = []
        if len(open_positions_dict) > 0:
            for p in open_positions_dict:
                bot_agents.append(p)
        
    except:
        bot_agents = []

    # Find ZSCORE triggerS
    for index, row in df.iterrows():

        # Extract variables
        base_market = row["base_market"]
        quote_market = row["quote_market"]
        hedge_ratio = row["hedge_ratio"]
        half_life = row["half_life"]
        intercept = row["intercept"]
    
        # Get Prices
        try:
            series_1 = get_candles_recent(client, base_market)
            series_2 = get_candles_recent(client, quote_market)

        except Exception as e:
            print(f"Error getting candles: {e}")
        
        # Get Zscore
        if len(series_1) > 0 and (len(series_1) == len(series_2)):
            spread = series_1 - (hedge_ratio * series_2 + intercept)
            z_score = calculate_zscore(spread).values.tolist()[-1]
        else:
            print("Data series are mismatched or empty.")
            continue
        # Establish if potential trade
        if abs(z_score) >= ZSCORE_THRESH:

            #  Ensure like-for-like not already open (diversify trading)
            is_base_open = is_open_positions(client, base_market)
            is_quote_open = is_open_positions(client, quote_market)

            # Place Trade
            if (not is_base_open) and (not is_quote_open):

                # Determine side
                base_side = "BUY" if z_score < 0 else "SELL"
                quote_side = "BUY" if z_score > 0 else "SELL"

                # Get acceptable price in string format with correct number of decimals
                base_price = series_1[-1]
                quote_price = series_2[-1]
                accept_base_price = float(base_price) * 1.01 if z_score < 0 else float(base_price) * 0.99
                accept_quote_price = float(quote_price) * 1.01 if z_score > 0 else float(quote_price) * 0.99
                failsafe_base_price = float(base_price) * 0.05 if z_score < 0 else float(base_price) * 1.7
                base_tick_size = markets["markets"][base_market]["tickSize"]
                quote_tick_size = markets["markets"][quote_market]["tickSize"]

                # Format prices
                accept_base_price = format_number(accept_base_price, base_tick_size)
                accept_quote_price = format_number(accept_quote_price, quote_tick_size)
                accept_failsafe_base_price = format_number(failsafe_base_price, base_tick_size)

                # Get size
                base_quantity = 1 / base_price * USD_PER_TRADE
                quote_quantity = 1 / quote_price * USD_PER_TRADE
                base_step_size = markets["markets"][base_market]["stepSize"]
                quote_step_size = markets["markets"][quote_market]["stepSize"]

                # Format sizes
                base_size = format_number(base_quantity, base_step_size)
                quote_size = format_number(quote_quantity, quote_step_size)


                # Ensure sizes
                base_min_order_size = markets["markets"][base_market]["minOrderSize"]
                quote_min_order_size = markets["markets"][quote_market]["minOrderSize"]
                check_base = float(base_quantity) > float(base_min_order_size)
                check_quote = float(quote_quantity) > float(quote_min_order_size)


                # If checks pass, place trades
                if (check_base and check_quote):

                    # Check account balance
                    try:
                        account = client.private.get_account()
                        free_collateral = float(account.data["account"]["freeCollateral"])
                        print('---')
                        print(f"Balance: {free_collateral} and minimum at {USD_MIN_COLLATERAL}")
                    except Exception as e:
                        print(f"Error with get_account:, {e}")

                    # Guard: ensure collateral
                    if free_collateral < USD_MIN_COLLATERAL:
                        print(f"Found another trade but not enough collateral: {base_market} {quote_market}")
                        break

                    # Create Bot Agent
                    bot_agent = BotAgent(
                        client,
                        market_1=base_market,
                        market_2=quote_market,
                        base_side=base_side,
                        base_size=base_size,
                        base_price=accept_base_price,
                        quote_side=quote_side,
                        quote_size=quote_size,
                        quote_price=accept_quote_price,
                        accept_failsafe_base_price=accept_failsafe_base_price,
                        z_score=z_score,
                        half_life=half_life,
                        hedge_ratio=hedge_ratio,
                        intercept=intercept,
                    )

                    # Open Trades
                    bot_open_dict = bot_agent.open_trades()

                    if bot_open_dict is None:
                        print("Failed to open trades, received no data.")
                        continue  # Skip this iteration or handle appropriately
                    
                    # Handles succes in opening trades
                    if bot_open_dict["pair_status"] == "live":
                        print("Appending to bot_agents list.")
                        # Append to list of bot agents
                        bot_agents.append(bot_open_dict)
                        print(f"Current number of agents: {len(bot_agents)}")
                        del(bot_open_dict)
                        
                        # Confirm live status in print
                        print("Trade status: Live")
                        print("---")
                    elif bot_open_dict.get("pair_status") == "failed":
                        continue
                else:
                    print(f"Quantity does not meet min order size. Move to next pair")
                    print(f"{base_market}: {check_base} and {quote_market}: {check_quote}")
                    print('---')
                    continue
    # Save Agents
    print(f"Success: Managed open trades.")
    if len(bot_agents) > 0:
        with open("bot_agents.json", "w") as f:
            json.dump(bot_agents, f)

                    
                                     

