from datetime import datetime, timedelta
import time
from pprint import pprint
from func_utils import format_number
import json


# Get existing open positions
def is_open_positions(client, market):

    # Protect API
    time.sleep(0.2)

    # Get positions
    all_positions = client.private.get_positions(
        market=market,
        status="OPEN",
    )

    # determine if open positions
    if len(all_positions.data["positions"])> 0:
        return True
    else:
        return False
        

# Check order status
def check_order_status(client, order_id):
    try:
        order = client.private.get_order_by_id(order_id)
        
        if "order" in order.data.keys():
                return order.data["order"]["status"]
        else:
            return "FAILED"
    except Exception as e:
        print(f"Error getting order status: {e}")
        return "FAILED"


# Place market order
def place_market_order(client, market, side, size, price, reduce_only):
    # get position id
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]

    # get expiration time
    server_time = client.public.get_time()
    expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "")) + timedelta(seconds=70)

    # place an order
    placed_order = client.private.create_order(
    position_id=position_id, # required for creating the order signature
    market=market,
    side=side,
    order_type="MARKET",
    post_only=False,
    size=size,
    price=price,
    limit_fee='0.015',
    expiration_epoch_seconds=expiration.timestamp(),
    time_in_force="FOK",
    reduce_only=reduce_only,
    )

    # return result
    return placed_order.data

def close_order(client, market, side, size, price):
    print("Attempting to close order...")
    try:
        close_order = place_market_order(
            client,
            market=market,
            side=side,
            size=size,
            price=price,
            reduce_only=True,
        )
        time.sleep(5)
        # Ensure order closure
        order_status = check_order_status(client, close_order["order"]["id"])
        if order_status == "FILLED":
            print(f"Successfully closed order in {market}")
        else:
            print(f"Failed to close order in {market}")
            raise Exception("Failed to close order")
    except Exception as e:
        print("ABORT Program")
        print("Unexpected Error in closing order:", e)
        raise

# ABORT all open positions
def abort_all_positions(client):
    
    # Cancel all orders
    client.private.cancel_all_orders()

    # Protect API
    time.sleep(0.5)

    # Get markets for reference of tick size
    markets = client.public.get_markets().data

    # pprint(markets)

    # Protect API
    time.sleep(0.5)

    # Get all open positions
    positions = client.private.get_positions(status="OPEN")
    all_positions = positions.data["positions"]

    # Handle open positions
    close_orders = []
    if len(all_positions) > 0:

        # Loop through each position
        for position in all_positions:

            # Determine Market
            market = position["market"]

            # Determine Side
            side = "BUY"
            if position["side"] == "LONG":
                side = "SELL"

            # print(market, side)
            #     get price
            price = float(position["entryPrice"])
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            tick_size = markets["markets"][market]["tickSize"]
            accept_price = format_number(accept_price, tick_size)

            # Place order
            order = place_market_order(
                client,
                market,
                side,
                position["sumOpen"],
                accept_price,
                True,
            )

            # Append the result
            close_orders.append(order)

            # Protect API
            time.sleep(0.5)

    # Empty the bot_agents.json file
    empty_bot_agents_json()

    # Return closed orders
    return close_orders

def empty_bot_agents_json():   
    # Open the file in write mode and write an empty list or object
    with open("bot_agents.json", "w") as file:
        json.dump([], file)  # Writes an empty list to the file

    print("bot_agents.json has been emptied.")
        