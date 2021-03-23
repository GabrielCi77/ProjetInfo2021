import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, timedelta

response = requests.get('https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm')
print(response.status_code)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', summary='Henry Hub Natural Gas Spot Price (Dollars per Million Btu)')
cases = table.find_all('td')
index=["lun","mar","mer","jeu","ven","sam","dim"]
semaine=[]
prix=[]
for i,td in enumerate(cases):
    if i%6==0:
        semaine.append(td.text)
    else:
        prix.append(td.text)


print(semaine)
with open('usaPrice.csv', 'a') as file:
    file.write('\n')
    file.write(f"{date_price},{price}")