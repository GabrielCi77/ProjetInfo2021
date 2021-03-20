import requests
from bs4 import BeautifulSoup
import pandas as pd
from progress.bar import Bar
"""
Donne un csv avec tous les bateaux LNG Tanker dans data.csv
On peut obtenir le MMSI et le IMO aussi grâce à l'url
Certains bateaux n'ont pas de MMSI et ils ne peuvent pas naviguer et il n'y a pas de destination disponible, on les enleve du csv
"""

def BoatInPage(url):
    """
    renvoie le nom, mmsi, imo et url des bateaux sur une page 
    
    Paramètres
    ----------
    url : string
        url de la page VesselFinder de recherche de navire à partir de laquelle on extrait les informations
    
    Retours
    -------
    DataFrame

    Exemple
    -------
    >>> df = BoatInPage(https://www.vesselfinder.com/fr/vessels?page=1&type=601)
    """
    df_bateau = pd.DataFrame(columns=["Nom Bateau", "IMO", "MMSI", "Lien"])
    try:
        requete = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
    except requests.exceptions.ConnectionError:
        return df_bateau
    else:
        soup = BeautifulSoup(requete.content, features="html.parser")
        liste_liens = soup.find_all('a', class_ = "ship-link")
    
    for item in liste_liens:
        type_bateau = item.find('div', class_ = "slty") #slty = Ship List TYpe
        if type_bateau.string == "LNG Tanker":
            url_bateau = item.get('href') #Lien vers la page VesselFinder du bateau
            nom_bateau = item.find('div', class_ = "slna") # slna = Ship List NAme
            indice_imo = url_bateau.find("IMO-")+4 #On cherche la position de l'IMO dans
            imo = url_bateau[indice_imo:indice_imo+7] # l'url pour l'extraire
            indice_mmsi = url_bateau.find("MMSI-")+5
            mmsi = url_bateau[indice_mmsi:]
            if mmsi != '0':
                # Ici seuls les bateaux en service sont selectionnés
                df_bateau = df_bateau.append({"Nom Bateau" : nom_bateau.string,
                                        "IMO": imo,
                                        "MMSI": mmsi,
                                        "Lien": "vesselfinder.com"+url_bateau },
                                        ignore_index=True)
    return df_bateau

def allBoat():
    """
    renvoie tous les noms, mmsi, imo et url de tous les bateaux
    référencés sur VesselFinder de type LNG Tanker

    Retours
    -------
    DataFrame
    """
    boat_type = "601" #LNG/LPG/CO2 Tanker
    allBoat_df = pd.DataFrame(columns=["Nom Bateau", "IMO", "MMSI", "Lien"])
    bar = Bar('Processing', max=130)
    for i in range(1, 131): #Il y a 130 pages de bateaux de type LNG Tanker sur VesselFinder
        url_page="https://www.vesselfinder.com/fr/vessels?page=" + str(i) + "&type=" + str(boat_type)
        allBoat_df = allBoat_df.append( BoatInPage(url_page), ignore_index=True)
        bar.next()
    bar.finish()
    return allBoat_df
 
new_boat_list = allBoat()
old_boat_list = pd.read_csv("data.csv")
x1, x2 = new_boat_list.shape[0], old_boat_list.shape[0]
if x1-x2:
    print(f"{x1-x2} nouveau(x) bateau(x) ajouté(s) à la liste")
    # lancer le programme pour récupérer la taille des navires
    new_boat_list.to_csv("data.csv", index=False)
else:
    print("Aucun nouveau bateau ajouté à la liste")