import numpy as np
import pandas as pd

if __name__ == '__main__':
    df = pd.read_csv('../data/loadAll_extended.csv')
    df = df.dropna(axis = 0, how = 'any', inplace = False)

    # df = df.groupby(['Atime'])[['D_SA', 'A_SA', 'D_AF', 'A_AF', 'D_OC', 'A_OC', 'D_NA', 'A_NA', 'D_AS', 'A_AS', 'D_EU', 'A_EU']].sum()
    # df = df.groupby(['Atime'])['A_EU', 'A_AS'].sum()
    df = df.groupby('Atime').agg({
        'D_EU' : ['sum'], 'D_NA' : ['sum'], 'D_AS' : ['sum'], 'A_EU' : ['sum'], 'A_NA' : ['sum'], 'A_AS' : ['sum'],
        'Eur_Spot_12' : ['min'], 'Eur_Spot_9' : ['min'], 'Eur_Spot_6' : ['min'], 'Eur_Spot_3' : ['min'], 'Eur_Spot_0' : ['min'], 'Eur_Spot_-3' : ['min'], 'Eur_Spot_-6' : ['min'], 'Eur_Spot_-9' : ['min'], 'Eur_Spot_-12' : ['min'], 'Eur_Spot_-15' : ['min'], 'Eur_Spot_-18' : ['min'], 'Eur_Spot_-21' : ['min'],
        'US_Spot_12' : ['min'], 'US_Spot_9' : ['min'], 'US_Spot_6' : ['min'], 'US_Spot_3' : ['min'], 'US_Spot_0' : ['min'], 'US_Spot_-3' : ['min'], 'US_Spot_-6' : ['min'], 'US_Spot_-9' : ['min'], 'US_Spot_-12' : ['min'], 'US_Spot_-15' : ['min'], 'US_Spot_-18' : ['min'], 'US_Spot_-21' : ['min'],
        'Asia_Fut_12' : ['min'], 'Asia_Fut_9' : ['min'], 'Asia_Fut_6' : ['min'], 'Asia_Fut_3' : ['min'], 'Asia_Fut_0' : ['min'], 'Asia_Fut_-3' : ['min'], 'Asia_Fut_-6' : ['min'], 'Asia_Fut_-9' : ['min'], 'Asia_Fut_-12' : ['min'], 'Asia_Fut_-15' : ['min'], 'Asia_Fut_-18' : ['min'], 'Asia_Fut_-21' : ['min']
        })

    # second_row = df.line[1]
    # df = df.drop([second_row], axis=0)

    df.to_csv('../data/loadAll_extended_agg_All.csv')
    