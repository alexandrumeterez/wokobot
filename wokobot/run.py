import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import os
import pandas as pd

EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

class Ad(object):
    def __init__(self, link, name, date_posted, date_start, address):
        self.link = link
        self.name = name
        self.date_posted = date_posted
        self.date_start = date_start
        # self.rent = rent
        self.address = address

    def as_string(self):
        result = f"Link: {self.link} for ad {self.name}, posted at {self.date_posted}. At {self.address} and starts on {self.date_start}"
        return result

    def as_list(self):
        result = [self.link, self.name, self.date_posted, self.date_start, self.address]
        return result

class WOKOParser(object):
    def __init__(self, url):
        self.url = url
        self.refresh()

    def pprint(self, soup_result):
        print(soup_result.prettify())

    def refresh(self):
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    def parse_ad(self, ad_div):
        link = 'woko.ch' + ad_div.find('a', href=True)['href']
        name = ad_div.find('h3').contents[0]
        date_posted = ad_div.find('span').contents[0]
        tds = ad_div.find_all('td')
        date_wanted = tds[1].contents[0].strip().split()[2]
        address = tds[-1].contents[0]
        return Ad(link, name, date_posted, date_wanted, address)

    def get_ads(self):
        result = self.soup.find('div', {'id': 'GruppeID_98'}).find_all('div', {'class': 'inserat'})
        parsed_ads = [self.parse_ad(ad) for ad in result]
        return parsed_ads

def send_mail(ads):
    msg = EmailMessage()
    content = f"Number of ads: {len(ads)}\n"
    content += '\n'.join([ad.as_string() for ad in ads])

    msg.set_content(content)
    msg['Subject'] = 'WOKO Ads'

    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == '__main__':
    parser = WOKOParser('http://woko.ch/en/nachmieter-gesucht')
    ads = parser.get_ads()
    list_ads = [ad.as_list() for ad in ads]

    new_ads = pd.DataFrame(list_ads, columns=['Link', 'Name', 'DatePosted', 'DateStart', 'Address'])
    if not os.path.exists('saved_ads.csv'):
        print('Fresh start, creating file now')
        new_ads.to_csv('saved_ads.csv', index=False)
        send_mail(ads)
    else:
        saved_ads = pd.read_csv('saved_ads.csv')
        if not new_ads.equals(saved_ads):
            print('New ads, sending email')
            send_mail(ads)