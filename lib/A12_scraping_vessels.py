import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import csv
from datetime import date
import contextlib
import pandas as pd
from A12_scraping_vessels_functions import separateSlash, convertDateYear, extractDestinationETA, extractOriginATD

'''
L'idée de ce programme est de scraper les données liées au trajet des navires sur le site 'vesselfinder.com'.
On dispose d'une liste des navires à scraper avec l'URL correspondant à chaque fois.
Pour chaque navire, on va donc se rendre sur la page web, scraper les données et les stocker dans une dataframe qu'on ajoute à la liste des dataframes.
A la fin, on fusionne toutes ces dataframes dans un seul fichier. Ainsi, on produit un fichier par exécution du programme.
On exécute ce programme une fois par jour afin d'avoir suffisamment de données pour la suite.
'''

# on aura besoin de la date plus tard donc on la stocke dès le début
today = date.today()
# Création de la liste des dataframes
list_df = []


'''
Commentaires E-CUBE (Marwane) : 
- Reprendre les commentaires des autres scripts
- separate_slash(string) : remplacer par string.split('/'), fonction native de Python --> FAIT
- S'il y a des copier-coller, il y a de fortes chances qu'il faille écrire des fonctions supplémentaires 
    Ex : convertdatewithyear et convertdate sont très similaires, peut-être appeler convertdate dans convertdatewithyear 
    plutôt que de copier-coller
'''



# On va ouvrir les pages correspondant à un navire et les scraper les unes après les autres
# On commence par ouvrir le fichier data.csv qui contient la liste de tous les navires avec leur URL
with open('../data/data.csv', newline='') as csv_file :
    content = csv.reader(csv_file)
    # On lit les lignes une par une :
    for row in content :
        if row[3] != 'Lien' : # pour ne pas lire l'en-tête du fichier
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
                    ATD = convertDateYear(ATD, False)
                    destination_brut = soup.find('div', class_= 'vi__r1 vi__sbt')
                    destination_brut = destination_brut.text
                    destination, ETA = extractDestinationETA(destination_brut)
                    ETA = convertDateYear(ETA, False)
                    # destination2 = value3.text
                    # destination2 = extractdestination2(destination2)
                    tirant = values2[1].text
                    tirant = tirant[:-2] # il faut enlever l'unité
                    # coordonnees = values2[9].text
                    direction, vitesse = separateSlash(values2[0].text)
                    statut = values2[2].text
                    date_position = soup.find(id='lastrep')['data-title'] # à convertir
                    date_position = convertDateYear(date_position, True)

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
                        ETA = convertDateYear(ETA, False)
                        # destination2 = value3.text
                        # destination2 = extractdestination2(destination2)
                        tirant = values2[1].text
                        tirant = tirant[:-2] # il faut enlever l'unité
                        # coordonnees = values2[9].text
                        direction, vitesse = separateSlash(values2[0].text)
                        statut = values2[2].text
                        date_position = soup.find(id='lastrep')['data-title'] # à convertir
                        date_position = convertDateYear(date_position, True)

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
df.to_csv(f'../data/donnees-navires/list-vessels-{today}.csv', index=False, mode='a')