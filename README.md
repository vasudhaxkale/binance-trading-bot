# binance-trading-bot
Python-based Binance Futures Testnet trading bot with GUI and CLI support. Supports market, limit, and stop-limit orders with full logging and error handling.
# Binance Futures Trading Bot (Testnet)

This project is a simplified yet powerful trading bot built in Python to interact with the **Binance Futures USDT-M Testnet**. It supports placing **Market**, **Limit**, and **Stop-Limit** orders through both:

- ✅ A user-friendly **Graphical User Interface (GUI)** built using `tkinter`
- ✅ A flexible **Command Line Interface (CLI)** using `argparse`

---

## 🚀 Features

- Connects to Binance Futures **Testnet**
- Supports:
  - `MARKET` orders
  - `LIMIT` orders
  - `STOP_LIMIT` orders
- Works for both **BUY** and **SELL** sides
- Dual interface: **GUI** (for convenience) and **CLI** (for scripting or automation)
- Robust **logging** with timestamps and error tracing (`bot.log`)
- Proper **input validation** and exception handling

---

🔐 Binance Testnet API Setup
Go to: https://testnet.binancefuture.com

Create or log in with your GitHub

Generate a Futures Testnet API Key & Secret

Enable Futures API permissions

Paste these credentials into the GUI or pass via CLI

---

💻 Usage
➤ GUI Mode
Launch GUI (no arguments):

bash
Copy
Edit
python gui_trading_bot.py
Fill in:

Your API Key and Secret

Symbol (e.g. BTCUSDT)

Order type (MARKET / LIMIT / STOP_LIMIT)

Quantity (e.g. 0.001)

Price and Stop Price (if applicable)

Then click Place Order.

➤ CLI Mode
Run with flags:

bash
Copy
Edit
python gui_trading_bot.py \
  --api-key YOUR_API_KEY \
  --api-secret YOUR_API_SECRET \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
For LIMIT / STOP_LIMIT:

bash
Copy
Edit
python gui_trading_bot.py \
  --api-key YOUR_API_KEY \
  --api-secret YOUR_API_SECRET \
  --symbol BTCUSDT \
  --side SELL \
  --type STOP_LIMIT \
  --quantity 0.002 \
  --price 65000 \
  --stop-price 64900

  
