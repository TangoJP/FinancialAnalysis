from bs4 import BeautifulSoup
import pandas as pd

with open('component_list.html', 'rb') as page:
    soup = BeautifulSoup(page, "html.parser")
    ticker_list = soup.select("a")
    tickers = [ticker.string for ticker in ticker_list]

tickers = [ticker.replace('NYSE:', '') for ticker in tickers]
tickers = [ticker.replace('NASDAQ:', '') for ticker in tickers]

tickers = pd.Series(tickers)
tickers.to_csv('component_list.csv', index=False)
