import numpy as np
import pandas as pd

if __name__ == '__main__':
    df = pd.read_csv('../data/loadAll_noEmptyLine.csv')

    # df = df.groupby(['Atime'])[['D_SA', 'A_SA', 'D_AF', 'A_AF', 'D_OC', 'A_OC', 'D_NA', 'A_NA', 'D_AS', 'A_AS', 'D_EU', 'A_EU']].sum()
    # df = df.groupby(['Atime'])['A_EU', 'A_AS'].sum()
    df = df.groupby('Atime').agg({'A_EU' : ['sum'], 'A_NA' : ['sum'], 'A_AS' : ['sum'], 'Eur_Spot_0' : ['min'], 'Eur_Spot_-3' : ['min'], 'Eur_Spot_-6' : ['min'], 'Eur_Spot_-9' : ['min'], 'Eur_Spot_-12' : ['min'], 'US_Spot_0' : ['min'], 'US_Spot_-3' : ['min'], 'US_Spot_-6' : ['min'], 'US_Spot_-9' : ['min'], 'US_Spot_-12' : ['min'], 'Asia_Fut_0' : ['min'], 'Asia_Fut_-3' : ['min'], 'Asia_Fut_-6' : ['min'], 'Asia_Fut_-9' : ['min'], 'Asia_Fut_-12' : ['min']})

    second_row = df.line[1]
    df = df.drop([second_row], axis=0)

    df.to_csv('../data/loadAll_agg_All_alt.csv')
    