import pandas as pd
import numpy as np
import requests
import os
from bs4 import BeautifulSoup


class CompanyInfoScraper:
    def __init__(self):
        self.data = None

    def scrape(self, *tickers):
        fields = ['Name', 'url', 'Sector', 'Industry', 'Employees',
                  'Description', 'Executive1', 'Executive2', 'Executive3',
                  'Executive4', 'Executive5']
        self.data = pd.DataFrame(index=tickers, columns=fields)

        for c, ticker in enumerate(tickers):
            print("%d Scraping information on %s..." % ((c+1), ticker))
            # Get HTML response from Yahoo Finance page
            url = 'https://finance.yahoo.com/quote/'+ ticker + '/profile'
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")

            company = {}

            # Scrap company name
            try:
                self.data.loc[ticker]['Name'] = soup.find('h3').text
            except:
                self.data.loc[ticker]['Name'] = "N/A"

            # Scrap company website url
            try:
                self.data.loc[ticker]['url'] = \
                                soup.find('p', class_="D(ib) W(47.727%) Pend(40px)")\
                                    .find('a', target="_blank").text
            except:
                self.data.loc[ticker]['url'] = "N/A"

            # Scrape company sector, industry, number of employees
            info_1 = soup.find('p', class_="D(ib) Va(t)")
            try:
                self.data.loc[ticker]['Sector'] = \
                        info_1.find('strong',attrs={"data-reactid":21}).text
            except:
                self.data.loc[ticker]['Sector'] = "N/A"

            try:
                self.data.loc[ticker]['Industry'] = \
                        info_1.find('strong', attrs={"data-reactid":25}).text
            except:
                self.data.loc[ticker]['Industry'] = "N/A"

            try:
                self.data.loc[ticker]['Employees'] = \
                        info_1.find('span', attrs={"data-reactid":30}).text
            except:
                self.data.loc[ticker]['Employees'] = "N/A"

            # Scrape company country -- to be implemented

            # Scrape the company description
            description = soup.find('p', class_='Mt(15px) Lh(1.6)')
            try:
                self.data.loc[ticker]['Description'] = description.text
            except:
                self.data.loc[ticker]['Description'] = "N/A"

            # Scrape info on top executives (5 of them)
            try:
                info_2 = soup.find('tbody').find_all('tr')[:5]
                executive_infos = ['name', 'title', 'pay', 'exercised', 'age']
                for i, tr in enumerate(info_2):     # iterate over executives
                    executive_rank = 'Executive' + str(i+1)
                    executive_data = {}

                    # fill in each info for the executive
                    tds = tr.find_all('td')
                    for j, td in enumerate(tds):
                        executive_data[executive_infos[j]] = td.text

                    # Store the executive info
                    self.data.loc[ticker][executive_rank] = executive_data
            except:
                pass
        return
