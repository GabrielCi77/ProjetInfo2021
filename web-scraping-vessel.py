import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import csv
from datetime import date
import contextlib
import pandas as pd

df = pd.DataFrame(columns=["Nom Bateau", "IMO", "MMSI", "Pavillon", "Longueur", "Largeur", "GT", "DWT", "Destination", "Destination2", "ETA", "Tirant d'eau actuel", "Coordonnees", "Direction", "Vitesse", "Statut", "Date scraping", "Date position"])
today = date.today()


# Fonctions qui servent au formatage des données brutes

def separate_slash(string):
    i = 0
    for car in string :
        if car == '/':
            ind = i
        i+=1
    return string[:ind-1], string[ind+2:]

def findmonth(string):
    if string == 'Jan':
        convmonth = '01'
    elif string == 'Feb':
        convmonth = '02'
    elif string == 'Mar':
        convmonth = '03'
    elif string == 'Apr':
        convmonth = '04'
    elif string == 'May':
        convmonth = '05'
    elif string == 'Jun':
        convmonth = '06'
    elif string == 'Jul':
        convmonth = '07'
    elif string == 'Aug':
        convmonth = '08'
    elif string == 'Sep':
        convmonth = '09'
    elif string == 'Oct':
        convmonth = '10'
    elif string == 'Nov':
        convmonth = '11'
    elif string == 'Dec':
        convmonth = '12'
    return convmonth

def convertdate(string):
    if string == '-':
        return string
    convmonth = findmonth(string[:3])
    i = 0
    ind = 0
    for car in string :
        if car == ',':
            ind = i
        i+=1
    convday = string[4:ind]
    if len(convday)==1:
        convday = '0'+convday
    convhour = string[ind+2:]
    return f'2021-{convmonth}-{convday}-{convhour}'

def convertdatewithyear(string):
    if string == '-':
        return string
    convmonth = findmonth(string[:3])
    i = 0
    ind = 0
    for car in string :
        if car == ',':
            ind = i
        i+=1
    convday = string[4:ind]
    if len(convday)==1:
        convday = '0'+ convday
    convyear = string[ind+2:ind+6]
    convhour = string[ind+7:ind+12]
    return f'{convyear}-{convmonth}-{convday}-{convhour}'

def extractdestination2(string):
    if string[0] in ['-', '.', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'] :
        return string
    else :
        string = string[2:]
        dest2 = ''
        for car in string :
            if car != ' ':
                dest2 += car
        return dest2


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

                    section_ship_info_all1 = soup.find_all('table', class_='tparams')
                    section_ship_info = section_ship_info_all1[0]
                    values1 = section_ship_info.find_all('td', class_='v3')
                    section_ship_info_all2 = soup.find_all('table', class_='aparams')
                    section_ship_info = section_ship_info_all2[0]
                    values2 = section_ship_info.find_all('td', class_='v3')

                    section_ship_info_alt1 = soup.find_all('div', id='port-calls')
                    section_ship_info = section_ship_info_alt1[0]
                    section_ship_info = section_ship_info.find_all('div')
                    # section_ship_info_alt1 = soup.find_all('table', class_='tparams npctable')
                    # section_ship_info = section_ship_info_alt1[0]
                    # value3 = section_ship_info.find('a')

                    nom_bateau = values1[1].text
                    imo = values1[0].text
                    mmsi = values2[4].text
                    mmsi = mmsi[10:] # on garde que le mmsi et pas l'imo
                    pavillon = values1[3].text
                    longueur = values1[7].text
                    largeur = values1[8].text
                    gt = values1[5].text
                    dwt = values1[6].text
                    # destination = values2[2].text
                    # destination2 = value3.text
                    # destination2 = extractdestination2(destination2)
                    # ETA = values2[3].text
                    # ETA = convertdate(ETA) # on convertit la date dans le bon format
                    tirant = values2[1].text
                    tirant = tirant[:-2] # on enlève l'unité
                    # coordonnees = values2[9].text
                    direction, vitesse = separate_slash(values2[0].text)
                    statut = values2[2].text
                    date_position = soup.find(id='lastrep')['data-title']
                    date_position = convertdatewithyear(date_position) # on convertit la date dans le bon format

                    df = df.append({"Nom Bateau" : nom_bateau,
                                        "IMO": imo,
                                        "MMSI": mmsi,
                                        "Pavillon": pavillon,
                                        "Longueur" : longueur,
                                        "Largeur" : largeur,
                                        "GT" : gt,
                                        "DWT" : dwt,
                                        # "Destination" : destination,
                                        # "Destination2" : destination2,
                                        # "ETA" : ETA,
                                        "Tirant d'eau actuel" : tirant,
                                        # "Coordonnees" : coordonnees,
                                        "Direction" : direction,
                                        "Vitesse" : vitesse,
                                        "Statut" : statut,
                                        "Date scraping" : today,
                                        "Date position" : date_position
                                        },
                                        ignore_index=True)
            
            except AttributeError:
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

                    # section_ship_info_alt1 = soup.find_all('table', class_='tparams npctable')
                    # section_ship_info = section_ship_info_alt1[0]
                    # value3 = section_ship_info.find('td', class_='n3ata')

                    nom_bateau = values1[1].text
                    imo = values1[0].text
                    mmsi = values2[4].text
                    mmsi = mmsi[10:] # on garde que le mmsi et pas l'imo
                    pavillon = values1[3].text
                    longueur = values1[7].text
                    largeur = values1[8].text
                    gt = values1[5].text
                    dwt = values1[6].text
                    # destination = values2[2].text
                    # destination2 = value3.text
                    # destination2 = extractdestination2(destination2)
                    # ETA = values2[3].text # à convertir
                    # ETA = convertdate(ETA)
                    tirant = values2[1].text
                    tirant = tirant[:-2] # il faut enlever l'unité
                    # coordonnees = values2[9].text
                    direction, vitesse = separate_slash(values2[0].text)
                    statut = values2[2].text
                    date_position = soup.find(id='lastrep')['data-title'] # à convertir
                    date_position = convertdatewithyear(date_position)

                    df = df.append({"Nom Bateau" : nom_bateau,
                                        "IMO": imo,
                                        "MMSI": mmsi,
                                        "Pavillon": pavillon,
                                        "Longueur" : longueur,
                                        "Largeur" : largeur,
                                        "GT" : gt,
                                        "DWT" : dwt,
                                        # "Destination" : destination,
                                        # "Destination2" : destination2,
                                        # "ETA" : ETA,
                                        "Tirant d'eau actuel" : tirant,
                                        # "Coordonnees" : coordonnees,
                                        "Direction" : direction,
                                        "Vitesse" : vitesse,
                                        "Statut" : statut,
                                        "Date scraping" : today,
                                        "Date position" : date_position
                                        },
                                        ignore_index=True)

            except IndexError :
                pass

df.to_csv(f'./vessel-list-{today}.csv', index=False, mode='a')