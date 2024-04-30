from func_private import place_market_order, check_order_status, close_order
from func_utils import format_number
from datetime import datetime, timedelta
import time
from pprint import pprint

# Class: agent for managing opening and closing trades
class BotAgent:

    """
        Primary function of bot agent handles opening trades and checking order status
    """

    # Init class
    def __init__(
            self,
            client,
            market_1,
            market_2,
            base_side,
            base_size,
            base_price,
            quote_side,
            quote_size,
            quote_price,
            accept_failsafe_base_price,
            z_score,
            half_life,
            hedge_ratio,
            intercept,
    ):
        
        # Initialize class variables
            # Initialize class variables
        self.client = client
        self.market_1 = market_1
        self.market_2 = market_2
        self.base_side = base_side
        self.base_size = base_size
        self.base_price = base_price
        self.quote_side = quote_side
        self.quote_size = quote_size
        self.quote_price = quote_price
        self.accept_failsafe_base_price = accept_failsafe_base_price
        self.z_score = z_score
        self.half_life = half_life
        self.hedge_ratio = hedge_ratio
        self.intercept = intercept

        # Initialize output variable
        # Pair status options are FAILED, LIVE, CLOSE, ERRROR
        self.order_dict = {
            "market_1": market_1,
            "market_2": market_2,
            "hedge_ratio": hedge_ratio,
            "z_score": z_score,
            "half_life": half_life,
            "intercept": intercept,
            "order_id_m1": "",
            "order_m1_size": base_size,
            "order_m1_side": base_side,
            "order_time_m1": "",
            "order_id_m2": "",
            "order_m2_size": quote_size,
            "order_m2_side": quote_side,
            "order_time_m2": "",
            "pair_status": "",
            "comments": "",
        }
     
     # Check order status by id
    def check_order_status_by_id(self, order_id):
        # Allow time to process
        time.sleep(5)
        # check order status
        order_status = check_order_status(self.client, order_id)

        # Guard: If order cancelled move onto next Pair
        if order_status == "CANCELED": 
            print(f"{self.market_1} vs {self.market_2} - Order cancelled...")
            self.order_dict["pair_status"] = "failed"
            return "failed"
        
        # Guard: If order not filled wait until order expiration
        if order_status != "FILLED":
            time.sleep(10)
            order_status = check_order_status(self.client, order_id)

            # Guard if order cancelled move onto next Pair
            if order_status == "CANCELED": 
                print(f"{self.market_1} vs {self.market_2} - Order cancelled...")
                self.order_dict["pair_status"] = "failed"
                return "failed"
        
            # Guard if not filled, cancel order
            if order_status != "FILLED":
                self.client.private.cancel_order(order_id=order_id)
                self.order_dict["pair_status"] = "failed"
                print(f"{self.market_1} vs {self.market_2} - Order cancelled...")
                return "failed"
        
        return "live"

    # Open Trades
    def open_trades(self):

        # Place Base Order
        base_order = self.place_and_confirm_order(
            market=self.market_1,
            side=self.base_side,
            size=self.base_size,
            price=self.base_price,
            order_key="order_id_m1",
        )
        # exit early if base order fails
        if not base_order:
            return self.order_dict
        # Place Quote Order
        
        quote_order = self.place_and_confirm_order(
        market=self.market_2,
        side=self.quote_side,
        size=self.quote_size,
        price=self.quote_price,
        order_key="order_id_m2",
          )
                # Get markets for referece of tick size   
        try:
            markets = self.client.public.get_markets().data
            if markets is None:
                raise ValueError("Invalide get_markets response")
    
        except Exception as e:
            print(f"Encountered an error: {e}")
            return None
        
        side_m1_sell = self.quote_side
        tick_size_m1 = markets["markets"][self.market_1]["tickSize"]
        accept_price_m1 = float(self.base_price) * 1.05 if side_m1_sell == "BUY" else float(self.base_price) * 0.95
        accept_price_m1 = format_number(accept_price_m1, tick_size_m1)
        
        if not quote_order:
            close_order(client = self.client,
                        market=self.market_1, 
                        side= self.quote_side, #opposite of base
                        size= self.base_size, 
                        price=accept_price_m1)
            return self.order_dict
        
        self.order_dict["pair_status"] = "live"
        self.order_dict["order_time_m1"] = datetime.now().isoformat()
        return self.order_dict


    def place_and_confirm_order(self, market, side, size, price, order_key):
        # Print status
        print("---")
        print(f"{market}: Placing order...")
        print(f"Side: {side}, Size: {size}. Price: {price}")
        print("---")

        try:
            order = place_market_order(
            self.client, 
            market=market, 
            side=side, 
            size=size, 
            price=price, 
            reduce_only=False
        )
        
            self.order_dict[order_key] = order["order"]["id"]
            self.order_dict[f"order_time_{order_key[-2:]}"] = datetime.now().isoformat()

            time.sleep(2)
            # Confirm order is filled
            if self.check_order_status_by_id(self.order_dict[order_key]) == "live":
                return True
        
        except Exception as e:
            self.order_dict["pair_status"] = "failed"
            self.order_dict["comments"] = f"Market {market}: {e}"
            print(f"Error trading: {market}, {e}")

        return False