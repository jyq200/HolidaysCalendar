from bs4 import BeautifulSoup
import requests
import pandas as pd
from robotparser import RobotFileParser

init_url = 'https://www.timeanddate.com/holidays/chad/?nojs=1'
headers = {'User-Agent': 'WasThereAHoliday'}


class HolidayScrapper:
    def __init__(self):
        self.rp = RobotFileParser()
        self.rp.set_url('https://www.timeanddate.com/robots.txt')
        self.rp.read()
        if not self.rp.can_fetch('WasThereAHoliday',init_url):
            raise RuntimeError('Scrapping forbidden due to robots.txt file')
        self.countries = self.get_countries(self.get_page(init_url))
        try:
            # removing entries which are not countries
            self.countries.remove('un')
        except ValueError:
            pass
        try:
            # removing entries which are not countries
            self.countries.remove('world')
        except ValueError:
            pass

    def get_data(self):
        all_data = pd.DataFrame()
        for cntr in self.countries:
            print 'Fetching data for ' + cntr
            try:
                url = 'https://www.timeanddate.com/holidays/' + cntr + '/2016#!hol=8389401'
                if not self.rp.can_fetch('WasThereAHoliday', url):
                    raise RuntimeError('Scrapping forbidden due to robots.txt file')
                soup = self.get_page('https://www.timeanddate.com/holidays/' + cntr + '/2016#!hol=8389401')
                html_table = soup.find('table')
                df_table = pd.read_html(str(html_table))[0]
                df_table['country'] = cntr
                all_data = all_data.append(df_table)
            except ValueError:
                print 'Problem occured when fetching data for ' + cntr
                pass
        return all_data

    @staticmethod
    def get_page(url):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'lxml')
        return soup

    @staticmethod
    def get_countries(soup):
        countries = []
        select_list = soup.find(id="co")
        for cntr in select_list.children:
            countries.append(cntr['value'])
        return countries


def main():
    HolidayScrapper().get_data().to_csv('holidays.csv', encoding='utf-8', index=False)

if __name__ == "__main__":
    # execute only if run as a script
    main()
