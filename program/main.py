from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES, MANAGE_EXITS
from func_connections import connect_dydx
from func_private import abort_all_positions
from func_public import construct_market_prices
from func_cointegration import store_cointegration_results
from func_entry_pairs import open_positions
from func_exit_pairs import manage_trade_exits
from verify_json_positions import verify_json_positions
import time

if __name__ == "__main__":
    
    # Connect to client
    try:
        client = connect_dydx()
    except Exception as e:
        print(e)
        print("Error connecting to client", e)
        exit(1) 

    try:
        verify_json_positions(client)

    except Exception as e:
        print(f"Problem verifying position: {e}")

    if ABORT_ALL_POSITIONS:
        try:
            print("Closing all positions...")
            close_orders = abort_all_positions(client)
        except Exception as e:
            print("Error closing all positions: ", e)
            exit(1)

    # Find Cointegrate Pairs
    if FIND_COINTEGRATED:

        # Construct Market Prices
        try:
                print("Fetching market prices, please allow 3 mins...")
                df_market_prices = construct_market_prices(client)
        except Exception as e:
                print("Error constructing market prices: ", e)
                exit(1)

        # Store Cointegrated Pairs
        try:
            if df_market_prices.empty or df_market_prices.shape[1] < 2:  # Check if there are at least two markets to compare
                print("Error: Not enough data to find cointegrated pairs.")
                exit(1)
            else:
                print("Storing cointegrated pairs...")
                stores_result = store_cointegration_results(df_market_prices)
                if stores_result != "saved":
                     print("Error saving cointegrated pairs")
                     exit(1)
        except Exception as e:
             print("Error saving cointegrated pairs: ", e)
             exit(1)


    while True:    
        if MANAGE_EXITS:
            # Construct Market Prices
            try:
                print("Managing Exits...")
                manage_trade_exits(client)
            except Exception as e:
                print("Error managing exiting positions ", e)
                exit(1)
        # Find Cointegrate Pairs
        if PLACE_TRADES:
            # Construct Market Prices
            try:
                print("Find trading opportunities")
                open_positions(client)
            except Exception as e:
                print("Error trading pairs: ", e)
                exit(1)
        print("Waiting so you can check json file")
        time.sleep(10)