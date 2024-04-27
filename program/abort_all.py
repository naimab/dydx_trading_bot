from func_connections import connect_dydx
from func_private import abort_all_positions

if __name__ == "__main__":
    
    # Connect to client
    try:
        client = connect_dydx()
    except Exception as e:
        print(e)
        print("Error connecting to client", e)
        exit(1) 

    # abort all open positioins
    try:
        print("Closing all positions...")
        close_orders = abort_all_positions(client)
    except Exception as e:
        print("Error closing all positions: ", e)
        exit(1)