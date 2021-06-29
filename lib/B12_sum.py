import numpy as np
import pandas as pd

if __name__ == '__main__':
    df = pd.read_csv('../data/loadAll_extended_D.csv')
    df = df.dropna(axis = 0, how = 'any', inplace = False)

    # df = df.groupby(['Atime'])[['D_SA', 'A_SA', 'D_AF', 'A_AF', 'D_OC', 'A_OC', 'D_NA', 'A_NA', 'D_AS', 'A_AS', 'D_EU', 'A_EU']].sum()
    # df = df.groupby(['Atime'])['A_EU', 'A_AS'].sum()
    df = df.groupby('Atime').agg({
        'D_EU' : ['sum'], 'D_NA' : ['sum'], 'D_AS' : ['sum'], 'A_EU' : ['sum'], 'A_NA' : ['sum'], 'A_AS' : ['sum'],
        'Eur_Spot_12' : ['mean'], 'Eur_Spot_9' : ['mean'], 'Eur_Spot_6' : ['mean'], 'Eur_Spot_3' : ['mean'], 'Eur_Spot_0' : ['mean'], 'Eur_Spot_-3' : ['mean'], 'Eur_Spot_-6' : ['mean'], 'Eur_Spot_-9' : ['mean'], 'Eur_Spot_-12' : ['mean'], 'Eur_Spot_-15' : ['mean'], 'Eur_Spot_-18' : ['mean'], 'Eur_Spot_-21' : ['mean'],
        'US_Spot_12' : ['mean'], 'US_Spot_9' : ['mean'], 'US_Spot_6' : ['mean'], 'US_Spot_3' : ['mean'], 'US_Spot_0' : ['mean'], 'US_Spot_-3' : ['mean'], 'US_Spot_-6' : ['mean'], 'US_Spot_-9' : ['mean'], 'US_Spot_-12' : ['mean'], 'US_Spot_-15' : ['mean'], 'US_Spot_-18' : ['mean'], 'US_Spot_-21' : ['mean'],
        'Asia_Fut_12' : ['mean'], 'Asia_Fut_9' : ['mean'], 'Asia_Fut_6' : ['mean'], 'Asia_Fut_3' : ['mean'], 'Asia_Fut_0' : ['mean'], 'Asia_Fut_-3' : ['mean'], 'Asia_Fut_-6' : ['mean'], 'Asia_Fut_-9' : ['mean'], 'Asia_Fut_-12' : ['mean'], 'Asia_Fut_-15' : ['mean'], 'Asia_Fut_-18' : ['mean'], 'Asia_Fut_-21' : ['mean'],
        'Eur_Fut_12' : ['mean'], 'Eur_Fut_9' : ['mean'], 'Eur_Fut_6' : ['mean'], 'Eur_Fut_3' : ['mean'], 'Eur_Fut_0' : ['mean'], 'Eur_Fut_-3' : ['mean'], 'Eur_Fut_-6' : ['mean'], 'Eur_Fut_-9' : ['mean'], 'Eur_Fut_-12' : ['mean'], 'Eur_Fut_-15' : ['mean'], 'Eur_Fut_-18' : ['mean'], 'Eur_Fut_-21' : ['mean']
        })

    # second_row = df.line[1]
    # df = df.drop([second_row], axis=0)

    df.to_csv('../data/loadAll_extended_D_agg_All2.csv')
    