import pandas as pd
import matplotlib.pyplot as plt


def changeBar(df):
    df = df.groupby('Atime').sum()
    ax = df.plot.bar(stacked=True)


if __name__ == '__main__':
    df = pd.read_csv('./data/loadAll_extended.csv')
    df = df.dropna(axis = 0, how = 'any', inplace = False)
    df = df[['Atime', 'D_NA', 'D_SA', 'D_AS', 'A_AS', 'D_OC', 'D_AF', 'D_EU', 'A_EU']]
    df = df[df['A_EU'] + df['D_EU'] <= 1]
    df = df[df['A_AS'] + df['D_AS'] <= 1]
    df_asia = df[df['A_AS'] == 1]
    print(df_asia.columns)
    df_asia.drop(columns=['A_AS', 'A_EU', 'D_OC', 'D_SA'], inplace=True)
    df_eur = df[df['A_EU'] == 1]
    df_eur.drop(columns=['A_AS', 'A_EU', 'D_AS'], inplace=True)


    changeBar(df_eur)
    changeBar(df_asia)
    plt.show()