#passe des ports calls aux voyages

import pandas as pd
import numpy as np

'''
Commentaires E-CUBE (Marwane) :

- Commentaires généraux :
    - Ne pas mélanger l'anglais et le français - l'usage est de coder en anglais, mais c'est à voir avec votre tuteur
    - Donner des noms plus compréhensibles aux :
        - Fonctions : les écrire sous la forme doSomething (ex : getEuropeGasPrices)
        - Objets : éviter les df/df2, préférer respectivement portcalls/df_portcalls
    
- Commentaires spécifiques à ce script : 
    - Reprendre les commentaires faits dans FuturesAsie.py
    - Ne pas hésiter à appliquer plusieurs méthodes d'affilée sur un même objet (voir code ajouté)
    - Utiliser iloc n'est pas la meilleure pratique (trop long, même si c'est facilement compréhensible) : préférer des méthodes 
    vectorielles qui agissent sur des lignes/colonnes entières plutôt que sur un élément du dataframe à chaque fois
'''
def voyage():
    df = pd.read_csv('./Portcalls/Portcalls.csv', index_col=['IMO'])
    df2 = pd.DataFrame(columns=['IMO', 'Dport', 'Dcountry', 'Dtime', 'Aport', 'Acountry', 'Atime'])
    imos = np.unique(df.index.to_numpy()) #Liste de tous les imos
    for imo in imos:
        boat = df.loc[imo]
        if len(boat.shape) == 2:
            #on ne traite pas les séries car il faut deux ports pour un voyage
            for i in range(boat.shape[0]-1):
                df2 = df2.append({'IMO' : imo,
                                  'Dport' : boat.iloc[i]['Port'],
                                  'Dcountry' : boat.iloc[i]['Country'],
                                  'Dtime' : boat.iloc[i]['Arrival'],
                                  'Aport' : boat.iloc[i+1]['Port'],
                                  'Acountry' : boat.iloc[i+1]['Country'],
                                  'Atime' : boat.iloc[i+1]['Arrival']}, ignore_index=True)
    df2.set_index('IMO', inplace=True)
    dfv = pd.read_csv('./PortCalls/voyages.csv', index_col='IMO')
    dff = pd.concat([dfv, df2])
    dff2 = dff.drop_duplicates()

    ### Ajout Marwane : les lignes 31 et 32 peuvent être concaténées comme suit : ###
    dff2 = pd.concat([dfv, df2]).drop_duplicates()
    ###
    dff2.to_csv('./PortCalls/voyages.csv')

if __name__ == '__main__':
    voyage()