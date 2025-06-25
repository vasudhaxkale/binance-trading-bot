import argparse
import logging
import sys
import tkinter as tk
from tkinter import messagebox
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('TradingBot')

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)
        if testnet:
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
        logger.info("Bot initialized with testnet mode: %s", testnet)
        
        # Verify connection
        try:
            account = self.client.futures_account()
            logger.info("Account balance: %.2f USDT", 
                        float(next(a for a in account['assets'] if a['asset'] == 'USDT')['availableBalance']))
        except Exception as e:
            logger.error("Connection test failed: %s", e)
            raise ConnectionError(f"Failed to connect to API: {e}")

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        """Place order with validation and error handling"""
        # Validate inputs
        symbol = symbol.strip().upper()
        if not symbol:
            raise ValueError("Symbol is required")
            
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError("Quantity must be a positive number")
        
        if order_type == ORDER_TYPE_LIMIT and not price:
            raise ValueError("Price required for limit orders")
        
        if order_type == ORDER_TYPE_STOP_LIMIT and (not price or not stop_price):
            raise ValueError("Both price and stop_price required for stop-limit orders")

        # Prepare order parameters
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'newOrderRespType': 'FULL'
        }

        # Add price-related parameters
        if order_type in [ORDER_TYPE_LIMIT, ORDER_TYPE_STOP_LIMIT]:
            params['price'] = str(price)
            params['timeInForce'] = TIME_IN_FORCE_GTC
            
        if order_type == ORDER_TYPE_STOP_LIMIT:
            params['stopPrice'] = str(stop_price)
        
        try:
            logger.info("Placing order: %s", params)
            response = self.client.futures_create_order(**params)
            logger.info("Order response: %s", response)
            return response
        except BinanceAPIException as e:
            logger.error("API error: %s - %s", e.status_code, e.message)
            raise
        except Exception as e:
            logger.exception("Unexpected error placing order")
            raise

def run_cli():
    """Command Line Interface"""
    parser = argparse.ArgumentParser(description='Binance Futures Trading Bot', 
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # API credentials
    parser.add_argument('--api-key', required=True, help='API Key')
    parser.add_argument('--api-secret', required=True, help='API Secret')
    
    # Order parameters
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g. BTCUSDT)')
    parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('--type', required=True, choices=['MARKET', 'LIMIT', 'STOP_LIMIT'], 
                        dest='order_type', default='MARKET', help='Order type')
    parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    
    # Optional parameters
    parser.add_argument('--price', type=float, help='Order price (required for LIMIT/STOP_LIMIT)')
    parser.add_argument('--stop-price', type=float, help='Stop price (required for STOP_LIMIT)')
    
    args = parser.parse_args()
    
    try:
        # Initialize bot
        bot = BasicBot(args.api_key, args.api_secret)
        
        # Map parameters to Binance constants
        side = SIDE_BUY if args.side == 'BUY' else SIDE_SELL
        order_type_mapping = {
            'MARKET': ORDER_TYPE_MARKET,
            'LIMIT': ORDER_TYPE_LIMIT,
            'STOP_LIMIT': ORDER_TYPE_STOP_LIMIT
        }
        order_type = order_type_mapping[args.order_type]
        
        # Place order
        response = bot.place_order(
            symbol=args.symbol,
            side=side,
            order_type=order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price
        )
        
        # Output results
        print("\n✅ ORDER EXECUTED SUCCESSFULLY")
        print("=" * 40)
        print(f"Order ID:      {response['orderId']}")
        print(f"Symbol:        {response['symbol']}")
        print(f"Side:          {response['side']}")
        print(f"Type:          {response['type']}")
        print(f"Quantity:      {response['origQty']}")
        
        if 'price' in response:
            print(f"Price:         {response['price']}")
        if 'stopPrice' in response:
            print(f"Stop Price:    {response['stopPrice']}")
            
        print(f"Status:        {response['status']}")
        print(f"Executed Qty:  {response['executedQty']}")
        print("=" * 40)
        
    except Exception as e:
        logger.error("Order failed: %s", e)
        print(f"\n❌ ORDER FAILED: {str(e)}")
        sys.exit(1)

class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Binance Futures Testnet Bot")
        self.root.geometry("500x400")
        
        # Create input fields
        self.create_widgets()
        
    def create_widgets(self):
        # API Key
        tk.Label(self.root, text="API Key:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.api_key = tk.Entry(self.root, width=40)
        self.api_key.grid(row=0, column=1, padx=5, pady=5)
        
        # API Secret
        tk.Label(self.root, text="API Secret:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.api_secret = tk.Entry(self.root, width=40, show="*")
        self.api_secret.grid(row=1, column=1, padx=5, pady=5)
        
        # Symbol
        tk.Label(self.root, text="Symbol:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.symbol = tk.Entry(self.root)
        self.symbol.grid(row=2, column=1, padx=5, pady=5)
        self.symbol.insert(0, "BTCUSDT")
        
        # Side
        tk.Label(self.root, text="Side:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.side_var = tk.StringVar(value="BUY")
        tk.OptionMenu(self.root, self.side_var, "BUY", "SELL").grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Order Type
        tk.Label(self.root, text="Order Type:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.type_var = tk.StringVar(value="MARKET")
        types = ["MARKET", "LIMIT", "STOP_LIMIT"]
        self.type_menu = tk.OptionMenu(self.root, self.type_var, *types)
        self.type_menu.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.type_var.trace_add("write", self.toggle_price_fields)
        
        # Quantity
        tk.Label(self.root, text="Quantity:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.quantity = tk.Entry(self.root)
        self.quantity.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        self.quantity.insert(0, "0.001")
        
        # Price (for LIMIT/STOP_LIMIT)
        tk.Label(self.root, text="Price:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.price = tk.Entry(self.root)
        self.price.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        self.price.insert(0, "0")
        
        # Stop Price (for STOP_LIMIT)
        tk.Label(self.root, text="Stop Price:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        self.stop_price = tk.Entry(self.root)
        self.stop_price.grid(row=7, column=1, sticky="w", padx=5, pady=5)
        self.stop_price.insert(0, "0")
        
        # Place Order button
        self.submit_btn = tk.Button(self.root, text="Place Order", command=self.place_order)
        self.submit_btn.grid(row=8, column=0, columnspan=2, pady=20)
        
        # Status label
        self.status = tk.Label(self.root, text="", fg="blue")
        self.status.grid(row=9, column=0, columnspan=2)
        
        # Initially hide price fields
        self.toggle_price_fields()
    
    def toggle_price_fields(self, *args):
        """Show/hide price fields based on order type"""
        order_type = self.type_var.get()
        
        if order_type == "MARKET":
            self.price.grid_remove()
            self.stop_price.grid_remove()
            tk.Label(self.root, text="Price:").grid_remove()
            tk.Label(self.root, text="Stop Price:").grid_remove()
        elif order_type == "LIMIT":
            self.price.grid()
            self.stop_price.grid_remove()
            tk.Label(self.root, text="Price:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
            tk.Label(self.root, text="Stop Price:").grid_remove()
        else:  # STOP_LIMIT
            self.price.grid()
            self.stop_price.grid()
            tk.Label(self.root, text="Price:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
            tk.Label(self.root, text="Stop Price:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
    
    def place_order(self):
        """Handle order placement from GUI"""
        try:
            # Get values from form
            api_key = self.api_key.get().strip()
            api_secret = self.api_secret.get().strip()
            symbol = self.symbol.get().strip()
            side = self.side_var.get()
            order_type = self.type_var.get()
            quantity = float(self.quantity.get().strip())
            price = float(self.price.get().strip()) if self.price.get().strip() else None
            stop_price = float(self.stop_price.get().strip()) if self.stop_price.get().strip() else None
            
            # Update status
            self.status.config(text="Processing order...", fg="blue")
            self.root.update()
            
            # Initialize bot
            bot = BasicBot(api_key, api_secret)
            
            # Map parameters to Binance constants
            side_enum = SIDE_BUY if side == "BUY" else SIDE_SELL
            type_mapping = {
                "MARKET": ORDER_TYPE_MARKET,
                "LIMIT": ORDER_TYPE_LIMIT,
                "STOP_LIMIT": ORDER_TYPE_STOP_LIMIT
            }
            order_type_enum = type_mapping[order_type]
            
            # Place order
            response = bot.place_order(
                symbol=symbol,
                side=side_enum,
                order_type=order_type_enum,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )
            
            # Show success message
            self.status.config(
                text=f"✅ Order {response['orderId']} placed successfully!\n"
                     f"{response['origQty']} {symbol} at {response.get('price', 'market price')}",
                fg="green"
            )
            
        except Exception as e:
            logger.error("GUI order failed: %s", e)
            self.status.config(text=f"❌ Error: {str(e)}", fg="red")

if __name__ == "__main__":
    # Determine if we're running CLI or GUI
    if len(sys.argv) > 1:
        run_cli()
    else:
        root = tk.Tk()
        app = TradingBotGUI(root)
        root.mainloop()