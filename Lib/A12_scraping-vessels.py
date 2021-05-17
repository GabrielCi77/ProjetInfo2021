import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import csv
from datetime import date
import contextlib
import pandas as pd

# df_columns=["Nom Bateau", "IMO", "MMSI", "Pavillon", "Longueur", "Largeur", "GT", "DWT", "Origine", "ATD", "Destination", "Destination2", "ETA", "Tirant d'eau actuel", "Coordonnees", "Direction", "Vitesse", "Statut", "Date scraping", "Date position"]
today = date.today()
list_df = []


'''
Commentaires E-CUBE (Marwane) : 
- Reprendre les commentaires des autres scripts
- separate_slash(string) : remplacer par string.split('/'), fonction native de Python --> FAIT
- S'il y a des copier-coller, il y a de fortes chances qu'il faille écrire des fonctions supplémentaires 
    Ex : convertdatewithyear et convertdate sont très similaires, peut-être appeler convertdate dans convertdatewithyear 
    plutôt que de copier-coller
'''

def separateSlash(string) :
    stringlist = string.split('/')
    word1 = stringlist[0]
    word2 = stringlist[1]
    return word1[:-1], word2[1:]

# On crée un dictionnaire pour remplacer les mois par leur numéro (par exemple Aug par 08)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_numbers = ["%.2d" % i for i in range(1, len(months)+1)]
dict_month = {months[i]: month_numbers[i] for i in range(len(months))}

def convertDate(string) :
    '''
    Convertit la date scrapée en format :
    YYYY-MM-DD-hh:mm
    '''
    # Si le string commence par '-' alors il n'y a pas d'info donc on ne fait rien
    if string[0] == '-' :
        return '-' # on retourne juste '-' pour supprimer les éventuels \n
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

def convertDateWithYear(string) :
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

# def extractdestination2(string):
#     if string[0] in ['-', '.', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'] :
#         return string
#     else :
#         string = string[2:]
#         dest2 = ''
#         for car in string :
#             if car != ' ' :
#                 dest2 += car
#         return dest2

def extractDestinationETA(string) :
    i = 0
    for i in range(len(string)) :
        if string[i:i+4] == "ETA:" or string[i:i+4] == "ATA:" :
            ind = i
        i+=1
    destination = string[1:ind-2]
    eta = string[ind+5:-1]
    return destination, eta

def extractOriginATD(string) :
    i = 0
    for i in range(len(string)) :
        if string[i:i+4] == "ATD:" or string[i:i+4] == "ATA:" :
            ind = i
        i+=1
    origin = string[1:ind-1]
    atd = string[ind+5:-2]
    return origin, atd


with open('../Data/data.csv', newline='') as csvfile :
    content = csv.reader(csvfile)
    for row in content :
        if row[3] != 'Lien' :
            try :
                URL = 'https://www.'+row[3]

                # Ouverture de la page web

                r = urllib.request.Request(URL, headers= {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

                with contextlib.closing(urllib.request.urlopen(r)) as page :
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
                    origin, ATD = extractOriginATD(origin_brut)
                    ATD = convertDate(ATD)
                    destination_brut = soup.find('div', class_= 'vi__r1 vi__sbt')
                    destination_brut = destination_brut.text
                    destination, ETA = extractDestinationETA(destination_brut)
                    ETA = convertDate(ETA)
                    # destination2 = value3.text
                    # destination2 = extractdestination2(destination2)
                    tirant = values2[1].text
                    tirant = tirant[:-2] # il faut enlever l'unité
                    # coordonnees = values2[9].text
                    direction, vitesse = separateSlash(values2[0].text)
                    statut = values2[2].text
                    date_position = soup.find(id='lastrep')['data-title'] # à convertir
                    date_position = convertDateWithYear(date_position)

                    list_df.append(pd.DataFrame({"Nom Bateau" : nom_bateau,
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
                                        "Destination2" : "",
                                        "ETA" : ETA,
                                        "Tirant d'eau actuel" : tirant,
                                        "Coordonnees" : "",
                                        "Direction" : direction,
                                        "Vitesse" : vitesse,
                                        "Statut" : statut,
                                        "Date scraping" : today,
                                        "Date position" : date_position
                                        }, index = ["IMO"]))
            
            except AttributeError :
                URL = 'https://www.'+row[3]

                # Ouverture de la page web

                r = urllib.request.Request(URL, headers= {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

                with contextlib.closing(urllib.request.urlopen(r)) as page :
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
                        destination, ETA = extractDestinationETA(destination_test)

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
                        destination, ETA = extractDestinationETA(destination_test)
                        ETA = convertDate(ETA)
                        # destination2 = value3.text
                        # destination2 = extractdestination2(destination2)
                        tirant = values2[1].text
                        tirant = tirant[:-2] # il faut enlever l'unité
                        # coordonnees = values2[9].text
                        direction, vitesse = separateSlash(values2[0].text)
                        statut = values2[2].text
                        date_position = soup.find(id='lastrep')['data-title'] # à convertir
                        date_position = convertDateWithYear(date_position)

                        list_df.append(pd.DataFrame({"Nom Bateau" : nom_bateau,
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
                                            index = ["IMO"]))

                    except IndexError :
                        print("IndexError int")
                        print(row[3])
                        pass

            except IndexError :
                    print("IndexError ext")
                    print(row[3])
                    pass

# On concatène toutes les dataframes créées
df = pd.concat(list_df)
# On crée le csv à partir de la dataframe
# Index = False évite l'affichage d'une première colonne avec IMO
df.to_csv(f'../Data/donnees-navires/list-vessels-{today}-test.csv', index=False, mode='a')s