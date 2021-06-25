import B1_first as f

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

df_trips = f.loadTripsAndPriceData()
df_trips = df_trips[(df_trips['Dcountry']==' Algeria') & (df_trips['A_EU'] + df_trips['A_AS'] == 1)]
df_trips.set_index(pd.to_datetime(df_trips['Atime']), inplace=True)
df_trips = df_trips[['A_EU']]

dfg = df_trips.groupby(pd.Grouper(level='Atime', freq='1D')).sum()
first, last = dfg.index[0], dfg.index[-1]
test = pd.DataFrame(index=pd.date_range(start=first, end=last))

df = test.combine(dfg, lambda x, y: x + y, 0)

def showMeanAndStd(df):
    rolling_mean = df.rolling(window = 12).mean()
    rolling_std = df.rolling(window = 12).std()
    plt.plot(df, color = 'blue', label = 'Origine')
    plt.plot(rolling_mean, color = 'red', label = 'Moyenne mobile')
    plt.plot(rolling_std, color = 'black', label = 'Ecart-type mobile')
    plt.legend(loc = 'best')
    plt.title('Moyenne et Ecart-type mobiles')
    plt.show()

def adFuller(df):
    result = adfuller(df['A_EU'])
    print('Statistiques ADF : {}'.format(result[0]))
    print('p-value : {}'.format(result[1]))
    print('Valeurs Critiques :')
    for key, value in result[4].items():
        print('\t{}: {}'.format(key, value))


def getStationnary(df):
    adFuller(df)
    showMeanAndStd(df)


def substractMean(df):
    return (df - df.rolling(window=12).mean()).dropna()


def expDecay(df):
    rolling_mean_exp_decay = df.ewm(halflife=12, min_periods=0, adjust=True).mean()
    df_exp_decay = df - rolling_mean_exp_decay
    df_exp_decay.dropna(inplace=True)
    return df_exp_decay


def logShift(df):
    df_shift = df - df.shift()
    df_shift.dropna(inplace=True)
    return df_shift

def test(df, df_s, plot=True):
    decomposition = seasonal_decompose(df) 
    model = ARIMA(df, order=(4,1,1))
    results = model.fit(disp=-1)
    if plot:
        plt.plot(df_s)
        plt.plot(results.fittedvalues, color='red')
    return results.fittedvalues


def revertLogShift(df):
    df_true = df + df.shift()
    df_true.dropna(inplace=True)
    return df_true


def compareModel(df_pred, df):
    df_true = revertLogShift(df_pred)
    df_cap = df_true.apply(lambda x: x if x>=0 else 0)
    plt.plot(df)
    plt.plot(df_cap)
    plt.plot(df_true)

if __name__ == '__main__':
    # Plutot toutes les mêmes alpha très bon
    # getStationnary(df)
    # getStationnary(substractMean(df))
    # getStationnary(expDecay(df))

    # Celle la a l'air mieux
    # getStationnary(logShift(df))

    df_shift = logShift(df)
    # plot_acf(df_shift)
    # suggère 0 et 1 seulementn(MA)

    # plot_pacf(df_shift)
    # plt.show()
    # Je dirais 4 du coup (AR)

    df_pred = test(df, df_shift, plot=False)
    compareModel(df_pred, df)
    plt.show()
