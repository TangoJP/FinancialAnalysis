import pandas as pd
import numpy as np
import requests
import os
from bs4 import BeautifulSoup
from scraper import CompanyInfoScraper

# Get list of iShares Biotech ETF components
f = 'iShares_list.txt'
with open(f, encoding="utf-8") as page:
    soup = BeautifulSoup(page, "html.parser")
    td_list = soup.find_all('td', class_=" colTicker col1")
    tickers = [td.text for td in td_list]
pd.Series(sorted(tickers)).to_csv('iShares_scraped_tickers.csv', index=False)

scraper = CompanyInfoScraper()
scraper.scrape(*tickers)

df = scraper.data
df = df.sort_index()

df.to_csv('iShares_IBB_descriptions.csv')
