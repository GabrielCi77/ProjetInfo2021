import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import csv
from datetime import date
import contextlib
import pandas as pd

df = pd.DataFrame(columns=["Nom Bateau", "IMO", "MMSI", "Pavillon", "Longueur", "Largeur", "GT", "DWT", "Origine", "ATD", "Destination", "Destination2", "ETA", "Tirant d'eau actuel", "Coordonnees", "Direction", "Vitesse", "Statut", "Date scraping", "Date position"])
today = date.today()

'''
Commentaires E-CUBE (Marwane) : 
- Reprendre les commentaires des autres scripts
- separate_slash(string) : remplacer par string.split('/'), fonction native de Python
- S'il y a des copier-coller, il y a de fortes chances qu'il faille écrire des fonctions supplémentaires 
    Ex : convertdatewithyear et convertdate sont très similaires, peut-être appeler convertdate dans convertdatewithyear 
    plutôt que de copier-coller
'''

def separate_slash(string):
    i = 0
    for car in string :
        if car == '/':
            ind = i
        i+=1
    return string[:ind-1], string[ind+2:]

dict_month = {}
dict_month['Jan']= '01'
dict_month['Feb']= '02'
dict_month['Mar']= '03'
dict_month['Apr']= '04'
dict_month['May']= '05'
dict_month['Jun']= '06'
dict_month['Jul']= '07'
dict_month['Aug']= '08'
dict_month['Sep']= '09'
dict_month['Oct']= '10'
dict_month['Nov']= '11'
dict_month['Dec']= '12'

def convertdate(string):
    if string[0] == '-':
        return '-'
    convmonth = dict_month[string[:3]]
    i = 0
    ind = 0
    for car in string :
        if car == ',':
            ind = i
        i+=1
    convday = string[4:ind]
    if len(convday)==1:
        convday = '0'+convday
    convhour = string[ind+2:ind+7]
    return f'2021-{convmonth}-{convday}-{convhour}'

def convertdatewithyear(string):
    if string[0] == '-':
        return '-'
    convmonth = dict_month[string[:3]]
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

def extract_destination_eta(string):
    i = 0
    for i in range(len(string)) :
        if string[i:i+4] == "ETA:" or string[i:i+4] == "ATA:" :
            ind = i
        i+=1
    destination = string[1:ind-2]
    eta = string[ind+5:-2]
    return destination, eta

def extract_origin_atd(string):
    i = 0
    for i in range(len(string)) :
        if string[i:i+4] == "ATD:" or string[i:i+4] == "ATA:" :
            ind = i
        i+=1
    origin = string[1:ind-1]
    atd = string[ind+5:-1]
    return origin, atd


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

                    nom_bateau = values1[1].text
                    imo = values1[0].text
                    mmsi = values2[4].text
                    mmsi = mmsi[10:] # on garde que le mmsi et pas l'imo
                    pavillon = values1[3].text
                    longueur = values1[7].text
                    largeur = values1[8].text
                    gt = values1[5].text
                    dwt = values1[6].text
                    origin_brut = soup.find('div', class_= 'vi__r1 vi__stp')
                    origin_brut = origin_brut.text
                    origin, ATD = extract_origin_atd(origin_brut)
                    ATD = convertdate(ATD)
                    destination_brut = soup.find('div', class_= 'vi__r1 vi__sbt')
                    destination_brut = destination_brut.text
                    destination, ETA = extract_destination_eta(destination_brut)
                    ETA = convertdate(ETA)
                    # destination2 = value3.text
                    # destination2 = extractdestination2(destination2)
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
                                        "Origine" : origin,
                                        "ATD" : ATD,
                                        "Destination" : destination,
                                        # "Destination2" : destination2,
                                        "ETA" : ETA,
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

                    try :
                        section_ship_info_all = soup.find_all('table', class_='tparams')
                        section_ship_info = section_ship_info_all[3]
                        values1 = section_ship_info.find_all('td', class_='v3')
                        section_ship_info = section_ship_info_all[2]
                        values2 = section_ship_info.find_all('td', class_='v3')

                        destination_test = soup.find('div', class_= 'vi__r1 vi__sbt')
                        destination_test = destination_test.text
                        destination, ETA = extract_destination_eta(destination_test)

                        nom_bateau = values1[1].text
                        imo = values1[0].text
                        mmsi = values2[4].text
                        mmsi = mmsi[10:] # on garde que le mmsi et pas l'imo
                        pavillon = values1[3].text
                        longueur = values1[7].text
                        largeur = values1[8].text
                        gt = values1[5].text
                        dwt = values1[6].text
                        destination_test = soup.find('div', class_= 'vi__r1 vi__sbt')
                        destination_test = destination_test.text
                        destination, ETA = extract_destination_eta(destination_test)
                        ETA = convertdate(ETA)
                        # destination2 = value3.text
                        # destination2 = extractdestination2(destination2)
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
                                            # "Origine" : origin,
                                            # "ATD" : ATD,
                                            "Destination" : destination,
                                            # "Destination2" : destination2,
                                            "ETA" : ETA,
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
                        print("IndexError int")
                        print(row[3])
                        pass

            except IndexError :
                    print("IndexError ext")
                    print(row[3])
                    pass


df.to_csv(f'./list-vessels-{today}.csv', index=False, mode='a')