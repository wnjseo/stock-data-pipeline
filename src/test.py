from extract_stock import get_active_tickers, get_last_dates, extract_daily_stock_info
from transform_stock import transform_daily_stock_price, transform_daily_stock_indicator
import yfinance as yf
from datetime import date

# tickers = get_active_tickers()
# last_dates = get_last_dates(tickers)
# stock_df, errors = extract_daily_stock_info(tickers, last_dates)
# price_df = transform_daily_stock_price(stock_df)
# indicator_df = transform_daily_stock_indicator(price_df, last_dates)

# zero_volume = price_df[price_df["volume"] == 0]
# zero_price = price_df[price_df["adj_close_price"] == 0]
# print(zero_volume[["ticker", "trade_date"]])
# print(zero_price[["ticker", "trade_date"]])

test = yf.download("AAPL", start='2026-08-10', end=date.today())
print(test)