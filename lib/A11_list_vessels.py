"""
Donne un csv avec tous les bateaux LNG Tanker dans data.csv
On obtient le MMSI et le IMO grâce à l'url
Certains bateaux n'ont pas de MMSI et ils ne peuvent pas naviguer et il n'y a pas de destination disponible, on les enleve du csv
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from progress.bar import Bar
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'


def getBoatInfo(url):
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
    >>> df = getBoatInfo(https://www.vesselfinder.com/fr/vessels?page=1&type=601)
    """

    try:
        request = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
    except requests.exceptions.ConnectionError:
        return pd.DataFrame()
    else:
        soup = BeautifulSoup(request.content, features="html.parser")
        # Liste avec les urls de tous les bateaux sur la page de recherche
        list_url = soup.find_all('a', class_="ship-link")

    # On itère sur tous les bateaux présents sur la page
    list_data = []
    for url in list_url:
        type_ship = url.find('div', class_="slty")  # slty = Ship List TYpe
        if type_ship.string == "LNG Tanker":
            # On ne sélectionne que les bateaux catégorisés LNG tanker
            url_ship = url.get('href')  # Lien vers la page VesselFinder du bateau
            name_ship = url.find('div', class_="slna")  # slna = Ship List NAme
            # On cherche la position de l'IMO dans l'url pour l'extraire
            # On doit prendre la dernière occurence car certains bateaux ont IMO dans leur nom
            indice_imo = url_ship.rfind("IMO-")+4
            imo = url_ship[indice_imo:indice_imo+7]
            # Idem avec le MMSI
            indice_mmsi = url_ship.rfind("MMSI-")+5
            mmsi = url_ship[indice_mmsi:]
            if mmsi != '0':
                # Ici seuls les bateaux en service sont selectionnés
                list_data.append([name_ship.string, imo, mmsi, "vesselfinder.com" + url_ship])

    df_ship = pd.DataFrame(data=list_data, columns=["Nom Bateau", "IMO", "MMSI", "Lien"])
    return df_ship


def getAllBoat():
    """
    renvoie tous les noms, mmsi, imo et url de tous les bateaux
    référencés sur VesselFinder de type LNG Tanker

    Retours
    -------
    DataFrame
    """
    boat_type = "601"  # LNG/LPG/CO2 Tanker
    list_df = []  # Contient tous les df des pages de recherche
    bar = Bar('Processing', max=130)
    for i in range(1, 131):  # Il y a 130 pages de bateaux de type LNG Tanker sur VesselFinder
        url_page = "https://www.vesselfinder.com/fr/vessels?page=" + str(i) + "&type=" + str(boat_type)
        list_df.append(getBoatInfo(url_page))
        bar.next()
    bar.finish()
    df_all_boat = pd.concat(list_df, ignore_index=True)
    return df_all_boat


def analyseAndWrite():
    """
    Cette fonction met à jour la liste des infos sur les navires (data.csv) et communique sur le terminal
    les différences entre la nouvelle et l'ancienne liste de navires. Elle met à jour la liste des remplacements
    de noms (remplacement.csv)
    """

    new_boat_list = getAllBoat()
    new_boat_list[['MMSI', 'IMO']] = new_boat_list[['MMSI', 'IMO']].astype(int)
    old_boat_list = pd.read_csv("../Data/data.csv")
    # Dataframe contenant tous les navires sans répétitions mais avec des doublons
    diff = new_boat_list.merge(old_boat_list, how='outer', indicator=True).loc[lambda x: x['_merge'] != 'both']

    if diff.size:
        # On met en forme la colonne _merge selon qu'un bateau a été ajouté ou supprimé de la liste initiale
        diff['_merge'] = np.where(diff['_merge'] == 'left_only', 'ajout', 'suppression')
        # new est un dataframe contenant les ajouts et old les suppressions
        new = diff.loc[lambda x: x['_merge'] == 'ajout']
        old = diff.loc[lambda x: x['_merge'] == 'suppression']

        # On itère sur les lignes de l'ancien df
        for old_i, old_row in old.iterrows():
            if old_row['IMO'] in new.values:
                # Si un IMO apparaît dans les deux df c'est que le nom a été modifié
                new['_merge'] = np.where(new['IMO'] == old_row['IMO'], f"remplace {old_row['Nom Bateau']}", new['_merge'])
                old.drop(old_i, inplace=True)
        # Diff ne contient ni répétition de ligne ni doublon
        diff = pd.concat([new, old], ignore_index=True)

        # Communication sur le terminal de la MAJ de la liste
        print(f"{diff.loc[lambda x : x['_merge'] == 'ajout'].shape[0]} bateau(x) ajouté(s) à la liste")
        print(f"{old.shape[0]} bateau(x) supprimé(s) de la liste")
        print(f"{new.loc[lambda x : x['_merge'] != 'ajout'].shape[0]} actualisation(s) de nom")
        print(diff)

        # Ecriture dans les deux fichiers cs
        new_boat_list.to_csv("../Data/data.csv", index=False)
        new.loc[lambda x: x['_merge'] != 'ajout'].to_csv("../Data/remplacement.csv", mode='a', header=False, index=False)
    else:
        print("Aucun nouveau bateau ajouté à la liste")


if __name__ == '__main__':
    analyseAndWrite()
