#passe des ports calls aux voyages

import pandas as pd
import numpy as np

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
    dff2.to_csv('./PortCalls/voyages.csv')

if __name__ == '__main__':
    voyage()