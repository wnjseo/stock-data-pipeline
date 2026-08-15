from datetime import date

BACKFILL_START_DATE = date(2015, 1, 1)

MAX_RETRIES = 3
RETRY_DELAY = 1
REQUEST_DELAY = 0.5
INDICATOR_LOOKBACK_DAYS = 119
REFRESH_LOOKBACK_DAYS = 2

PRICE_COLUMNS = [
    "ticker",
    "trade_date",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "adj_close_price",
    "volume",
    "ohlc_valid"
]

HISTORY_COLUMNS = [
    "ticker",
    "trade_date",
    "adj_close_price",
    "volume"
]

INDICATOR_COLUMNS = [
    "ticker", 
    "trade_date", 
    "daily_return", 
    "volume_change_rate", 
    "ma5", 
    "ma20", 
    "ma60", 
    "ma120"
]

COMPANY_COLUMNS = [
    "ticker",
    "company_name",
    "sector",
    "industry",
    "country",
    "exchange"
]