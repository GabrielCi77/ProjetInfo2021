import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import csv
from datetime import date
import contextlib
import pandas as pd

df = pd.DataFrame(columns=["Nom Bateau", "IMO", "MMSI", "Pavillon", "Longueur", "Largeur", "GT", "DWT", "Destination", "ETA", "Tirant d'eau actuel", "Coordonnees", "Direction", "Vitesse", "Date scraping", "Date position"])

def separate_slash(string):
    i = 0
    for car in string :
        if car == '/':
            ind = i
        i+=1
    return string[:ind-1], string[ind+1:]

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
                    section_ship_info = section_ship_info_all[3]
                    values1 = section_ship_info.find_all('td', class_='v3')
                    section_ship_info = section_ship_info_all[2]
                    values2 = section_ship_info.find_all('td', class_='v3')

                    nom_bateau = values1[1].text
                    imo = values1[0].text
                    mmsi = values2[4].text
                    mmsi = mmsi[10:] # on garde que le mmsi et pas l'imo
                    pavillon = values1[3].text
                    longueur = values1[7].text
                    largeur = values1[8].text
                    gt = values1[5].text
                    dwt = values1[6].text
                    destination = values2[2].text
                    ETA = values2[3].text # à convertir
                    tirant = values2[7].text
                    tirant = tirant[:-2] # il faut enlever l'unité
                    coordonnees = values2[9].text
                    direction, vitesse = separate_slash(values2[8].text)
                    date_position = soup.find(id='lastrep')['data-title']
                    today = date.today()

                    df = df.append({"Nom Bateau" : nom_bateau,
                                        "IMO": imo,
                                        "MMSI": mmsi,
                                        "Pavillon": pavillon,
                                        "Longueur" : longueur,
                                        "Largeur" : largeur,
                                        "GT" : gt,
                                        "DWT" : dwt,
                                        "Destination" : destination,
                                        "ETA" : ETA,
                                        "Tirant d'eau actuel" : tirant,
                                        "Coordonnees" : coordonnees,
                                        "Direction" : direction,
                                        "Vitesse" : vitesse,
                                        "Date scraping" : today,
                                        "Date position" : date_position
                                        },
                                        ignore_index=True)
                    
                    
            except IndexError :
                pass
            except TypeError :
                pass

df.to_csv(f'./vessel-list-{today}.csv', index=False, mode='a')