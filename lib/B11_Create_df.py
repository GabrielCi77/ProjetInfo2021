from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import pandas as pd
from sklearn.linear_model import LinearRegression as LR
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np


producers = [
    # ' Qatar',
    ' United States (USA)',
    ' Nigeria',
    ' Algeria',
    #  ' Canada', on n'a pas le canada ?
    #  ' Norway',
    ' Russia',
    #  ' Mozambique', idem
    # ' Indonesia',
    #  ' Australia'
]

cn_to_ca2 = {
    # Bad country name to country alpha 2
    'United Arab Emirates (UAE)': 'AE',
    'Korea': 'KR',  # South Korea
    'Trinidad & Tobago': 'TT',
    'United States (USA)': 'US',
    'United Kingdom (UK)': 'GB',
    "Cote d'Ivoire": 'CI',
}

price_of_country = {
    'NA': 'America',  # North America
    'SA': 'America',  # South America
    'AS': 'Asia',  # Asia
    'OC': 'Asia',  # Australia
    'AF': 'Europe',  # Africa
    'EU': 'Europe',  # Europe
}


def convertNameToCode(country_name, continent):
    # Permet de passer de noms de pays dans nos documents à un code correspondant à un continent
    try:
        # code a deux lettres du pays
        calpha2 = country_name_to_country_alpha2(country_name.strip())
    except KeyError:
        # Certains noms de pays de nos jeux de données ne respectent pas la norme dispo sur wikipedia
        # https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        calpha2 = cn_to_ca2[country_name.strip()]
    # par exemple 'EU'
    concode = country_alpha2_to_continent_code(calpha2)
    return int(concode == continent)


def changeDate(date_str):
    return datetime.strptime(date_str, "%m/%d, %H:%M").strftime("2021-%m-%d")


def loadTripsAndPriceData():
    df_trips = pd.read_csv('./Data/Portcalls/voyages.csv')
    # On ajoute des colonnes avec les codes des pays de départ et d'arrivée
    for continent in price_of_country.keys():
        df_trips[f'D_{continent}'] = df_trips['Dcountry'].apply(convertNameToCode, args=(continent,))
        df_trips[f'A_{continent}'] = df_trips['Acountry'].apply(convertNameToCode, args=(continent,))
    # On modifie l'écriture des dates de départ et d'arrivées pour matcher celle des prix Europe
    df_trips['Dtime'] = df_trips['Dtime'].apply(changeDate)
    df_trips['Atime'] = df_trips['Atime'].apply(changeDate)

    # On charge les prix spots de l'Europe
    df_eur_price = pd.read_csv('./Data/SpotEur.csv', index_col='Date')
    # On ajoute les prix de l'Europe quand le bateau arrive et on normalise
    df_trips['Eur_Price'] = df_trips['Dtime'].apply(lambda x: df_eur_price.loc[x, 'Prix'])
    """ max_price_eur = df_trips['Eur_Price'].max()
    df_trips['Eur_Price'] = df_trips['Eur_Price'].apply(lambda x: x/max_price_eur) """

    """ # On charge les prix spot des US
    df_us_spot = pd.read_csv('./Data/SpotUS.csv', index_col='Date')
    df_trips['US_Price'] = df_trips['Dtime'].apply(mergeUSPrice, args=(df_us_spot,)) """
    """ max_price_us = df_trips['US_Price'].max()
    df_trips['US_Price'] = df_trips['US_Price'].apply(lambda x: x/max_price_us) """

    df_asia_fut = pd.read_csv('./Data/FuturesAsie.csv', index_col='Update date (CT)')
    months = 3
    for i in range(1, months+1):
        print(i)
        df_trips[f'Asia_Price_+{i}'] = df_trips['Dtime'].apply(mergeAsiaFutures, args=(i, df_asia_fut,))
    return df_trips


def findNearestDate(date_str, df_price):
    # On obtient une liste des dates où il y a des prix dans un format permettant de calculer
    # la distance à notre date date_str (qu'on convertira dans le même format)
    price_dates = pd.to_datetime(df_price.index).values
    # On calcule la date la plus proche en valeur absolue
    pivot = np.datetime64(date_str)
    nearest_date = min(price_dates, key=lambda x: abs(x - pivot))
    # On la transforme en string dans le même format que dans le dataframe df_price
    return np.datetime_as_string(nearest_date, unit='D')


def mergeUSPrice(date_str, df_price):
    # Pour les US c'est simple il faut renvoyer le prix correspondant à la date souhaitée
    return df_price.loc[findNearestDate(date_str, df_price), 'Prix US']


def mergeAsiaFutures(date_str, n_month, df_price):
    # On souhaite renvoyer n_months mois suivant la date du prix
    # Ex: prix le 3 février -> on renvoie le prix de mars et avril
    up_date = findNearestDate(date_str, df_price)
                
    # On réduit le df pour ne garder que les prix mis à jour le up_date
    df = df_price.loc[up_date]

    # On prend le mois qui se situe n_month après up_date
    dt_month = (datetime.strptime(up_date, "%Y-%m-%d") + timedelta(days=n_month*31))
    str_month = dt_month.strftime("%Y-%m")

    # On renvoie la valeur associé au mois
    if not df[df['Month'] == str_month].empty:
        return df[df['Month'] == str_month]['Prior Settle'].values[0]
    else:
        return np.nan


def addFuturesAsia(df):
    df_fut_asia = pd.read_csv('./Data/FuturesAsie.csv')
    print(df_fut_asia.head())
    df = loadTripsAndPriceData()
    df.to_csv('./Data/full.csv')

addFuturesAsia(pd.DataFrame())


""" def mergeUSPrice(date_str, df_price):
    i = 0
    if date_str not in df_price.index.values:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if date.weekday()==5:
            # Samedi -> lundi
            date = date + timedelta(days=2)
        else:
            # Dimanche ou autre -> lundi ou autre
            date = date + timedelta(days=1)
        date_str = date.strftime("%Y-%m-%d")
        i += 1
        if i > 10:
            return 3.00
    return df_price.loc[date_str, 'Prix US'] """