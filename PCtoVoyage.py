# Passe des ports calls aux voyages

import pandas as pd
import numpy as np
import time

'''
Commentaires E-CUBE (Marwane) :

- Commentaires généraux :
    - Ne pas mélanger l'anglais et le français - l'usage est de coder en anglais, mais c'est à voir avec votre tuteur
    - Donner des noms plus compréhensibles aux :
        - Fonctions : les écrire sous la forme doSomething (ex : getEuropeGasPrices)
        - Objets : éviter les df_portcalls/df_new_trips, préférer respectivement portcalls/df_portcalls

- Commentaires spécifiques à ce script:
    - Reprendre les commentaires faits dans FuturesAsie.py
    - Ne pas hésiter à appliquer plusieurs méthodes d'affilée sur un même objet (voir code ajouté)
    - Utiliser iloc n'est pas la meilleure pratique (trop long, même si c'est facilement compréhensible) : préférer des méthodes
    vectorielles qui agissent sur des lignes/colonnes entières plutôt que sur un élément du dataframe à chaque fois
'''


def createTrips():
    # On importe le fichier avec tous les appels de ports
    df_portcalls = pd.read_csv('./Portcalls/Portcalls.csv', index_col=['IMO'])

    timeA = time.time()
    list_data = []
    imo_list = np.unique(df_portcalls.index.to_numpy())  # Liste de tous les imo_list
    for imo in imo_list:
        ship = df_portcalls.loc[imo]
        if len(ship.shape) == 2:
            #  on ne traite pas les séries car il faut deux ports pour un voyage
            for i in range(ship.shape[0]-1):
                list_data.append([imo, ship.iloc[i]['Port'], ship.iloc[i]['Country'], ship.iloc[i]['Arrival'],
                                  ship.iloc[i+1]['Port'], ship.iloc[i+1]['Country'], ship.iloc[i+1]['Arrival']])

    # On crée un dataframe avec toutes ces informations
    df_columns = ['IMO', 'Dport', 'Dcountry', 'Dtime', 'Aport', 'Acountry', 'Atime']
    df_new_trips = pd.DataFrame(data=list_data, columns=df_columns)

    # On utilise IMO comme index pour concaténer ensuite avec l'autre
    df_new_trips.set_index('IMO', inplace=True)
    # On concatene et on sauvegarde dans le csv voyages
    df_old_trips = pd.read_csv('./PortCalls/voyages.csv', index_col='IMO')
    df_all_trips_unique = pd.concat([df_old_trips, df_new_trips]).drop_duplicates()
    df_all_trips_unique.to_csv('./PortCalls/voyages.csv')


if __name__ == '__main__':
    createTrips()
