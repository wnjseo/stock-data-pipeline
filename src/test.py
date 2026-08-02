from extract_stock import get_active_tickers, get_last_dates, extract_daily_stock_info
from transform_stock import transform_daily_stock_price, transform_daily_stock_indicator

tickers = get_active_tickers()[:5]
last_dates = get_last_dates(tickers)
stock_df, errors = extract_daily_stock_info(tickers, last_dates)
price_df = transform_daily_stock_price(stock_df)
indicator_df = transform_daily_stock_indicator(price_df, last_dates)

print(price_df)
print(indicator_df)
print(errors)
print(indicator_df[indicator_df["ticker"] == "MMM"].iloc[115:125][["trade_date", "ma120"]])