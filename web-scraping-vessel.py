import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import csv
from datetime import date
import contextlib


with open('data.csv', newline='') as csvfile:
    content = csv.reader(csvfile)
    for row in content :
        if row[3] != 'Lien' :
            try :
                URL = 'https://www.'+row[3]

                # Ouverture de la page web

                r = urllib.request.Request(URL, headers= {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

                with contextlib.closing(urllib.request.urlopen(r)) as page:
                    soup = BeautifulSoup(page, 'html.parser')


                    # Informations sur le navire

                    section_ship_info_all = soup.find_all('table', class_='tparams')
                    section_ship_info = section_ship_info_all[2]

                    labels = section_ship_info.find_all('td', class_='n3')
                    values = section_ship_info.find_all('td', class_='v3')

                    # On extrait les valeurs
                    # D'abord on prend la date de l'extraction
                    today = date.today()
                    update_date = soup.find(id='lastrep')['data-title']

                    list_labels = ["Date scraping", "Date maj"]
                    list_values = [today, update_date]

                    for label in labels :
                        list_labels.append(label.text)

                    for value in values :
                        list_values.append(value.text)


                    # On extrait la capacité du navire

                    section_ship_info = section_ship_info_all[3]

                    labels = section_ship_info.find_all('td', class_='n3')
                    values = section_ship_info.find_all('td', class_='v3')

                    list_labels.append(labels[5].text)
                    list_labels.append(labels[6].text)
                    list_values.append(values[5].text)
                    list_values.append(values[6].text)

                    # On écrit dans un fichier csv
                    with open(f'./vessel-info-list-test4-{today}.csv', 'a') as csv_file:
                        csv_writer = csv.writer(csv_file, dialect='excel')
                        csv_writer.writerows(zip(list_labels, list_values))
            except IndexError :
                pass
            except TypeError :
                pass