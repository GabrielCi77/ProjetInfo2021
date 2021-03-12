import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import csv

# Ouverture de la page web

URL = 'https://www.vesselfinder.com/fr/vessels/LNG-ALLIANCE-IMO-9320075-MMSI-228333700'

r = urllib.request.Request(URL, headers= {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
page = urllib.request.urlopen(r)
soup = BeautifulSoup(page, 'html.parser')


# Informations sur le navire

section_ship_info = soup.find_all('table', class_='tparams')
section_ship_info = section_ship_info[2]

labels = section_ship_info.find_all('td', class_='n3')
values = section_ship_info.find_all('td', class_='v3')

# On extrait les valeurs
# D'abord on prend la date de l'extraction
update_date = soup.find(id='lastrep')['data-title']

list_labels = ["Date maj"]
list_values = [update_date]

for label in labels :
    list_labels.append(label.text)

for value in values :
    list_values.append(value.text)

# On écrit dans un fichier csv
with open('./vessel-info.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file, dialect='excel')
    csv_writer.writerows(zip(list_labels, list_values))