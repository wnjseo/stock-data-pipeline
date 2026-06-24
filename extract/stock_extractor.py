import yfinance as yf

ticker = 'TSLA'
data = yf.download(ticker, period='1d')

print(data.head())