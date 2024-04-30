from dydx3.constants import API_HOST_SEPOLIA, API_HOST_MAINNET
from decouple import config

# SELECT MODE
MODE = "DEVELOPMENT"

# Close all open position and orders
ABORT_ALL_POSITIONS = False

# Find Cointegrated Pairs
# Set up OS function to check if exists
FIND_COINTEGRATED = False

# Place Trades
PLACE_TRADES = False

MANAGE_EXITS = True

# Resolution
RESOLUTION = "1HOUR"

# stats Window
WINDOW = 21

# Thresholds - Opening
MAX_HALF_LIFE = 24
ZSCORE_THRESH = 1.5
USD_PER_TRADE  =50
USD_MIN_COLLATERAL = 1750

# Thresholds - Closing
CLOSE_AT_ZSCORE_CROSS = True

ETHEREUM_ADDRESS = "0x96F8Fc28FAE2fbd3A9247CE838cFEaFb2178B71B"

# Must be on Mainnet on DYDX
STARK_PRIVATE_KEY_MAINNET=config("STARK_PRIVATE_KEY_MAINNET")
DYDX_API_KEY_MAINNET=config("DYDX_API_KEY_MAINNET")
DYDX_API_SECRET_MAINNET=config("DYDX_API_SECRET_MAINNET")
DYDX_API_PASSPHRASE_MAINNET=config("DYDX_API_PASSPHRASE_MAINNET")

# KEYS - Development
# Must be on Testnet on DYDX
STARK_PRIVATE_KEY_TESTNET=config("STARK_PRIVATE_KEY_TESTNET")
DYDX_API_KEY_TESTNET=config("DYDX_API_KEY_TESTNET")
DYDX_API_SECRET_TESTNET=config("DYDX_API_SECRET_TESTNET")
DYDX_API_PASSPHRASE_TESTNET=config("DYDX_API_PASSPHRASE_TESTNET")

# KEYS - Export
STARK_PRIVATE_KEY = STARK_PRIVATE_KEY_MAINNET if MODE == "PRODUCTION" else STARK_PRIVATE_KEY_TESTNET
DYDX_API_KEY = DYDX_API_KEY_MAINNET if MODE == "PRODUCTION" else DYDX_API_KEY_TESTNET
DYDX_API_SECRET = DYDX_API_SECRET_MAINNET if MODE == "PRODUCTION" else DYDX_API_SECRET_TESTNET
DYDX_API_PASSPHRASE = DYDX_API_PASSPHRASE_MAINNET if MODE == "PRODUCTION" else DYDX_API_PASSPHRASE_TESTNET

# HOST EXPORT
API_HOST = API_HOST_MAINNET if MODE == "PRODUCTION" else API_HOST_SEPOLIA

# HTTP PROVIDER
HTTP_PROVIDER_MAINNET = "http://localhost:8545"
HTTP_PROVIDER_TESTNET = "https://sepolia.infura.io/v3/504c3eae6b4e44379eadd5818d7b5d91"
HTTP_PROVIDER = HTTP_PROVIDER_MAINNET if MODE == "PRODUCTION" else HTTP_PROVIDER_TESTNET

