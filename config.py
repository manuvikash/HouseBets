import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot Settings
INITIAL_BALANCE = int(os.getenv("INITIAL_BALANCE", 1000))
CURRENCY_NAME = os.getenv("CURRENCY_NAME", "Bucks")
FEED_CHANNEL_NAME = os.getenv("FEED_CHANNEL_NAME", "housebets-feed")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/housebets.db")

# AMM Settings
INITIAL_LIQUIDITY = 100  # Initial liquidity parameter for each outcome
