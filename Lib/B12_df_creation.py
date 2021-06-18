from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from time import time

cn_to_ca2 = {
    # Bad country name to country alpha 2
    'United Arab Emirates (UAE)': 'AE',
    'Korea': 'KR',  # South Korea
    'Trinidad & Tobago': 'TT',
    'United States (USA)': 'US',
    'United Kingdom (UK)': 'GB',
    "Cote d'Ivoire": 'CI', }

continents = [
    'NA',  # North America
    'SA',  # South America
    'AS',  # Asia
    'OC',  # Australia
    'AF',  # Africa
    'EU',  # Europe
]


def isInContinent(country_name: str, continent: str):
    """Permet de vérifier si le pays est dans un continent

    Paramètres
    ----------
    country_name : str
        Le nom du pays
    continent : str
        Le code du continent (alpha2)

    Retours
    -------
    is_in_continent : int
        entier binaire positif si le pays est dans le continent

    Exemples
    -------
    >>> isInContinent('Gladstone', 'OC')
    1
    """
    try:
        # code a deux lettres du pays
        calpha2 = country_name_to_country_alpha2(country_name.strip())
    except KeyError:
        # Certains noms de pays de nos jeux de données ne respectent pas la norme dispo sur
        # wikipedia : https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        calpha2 = cn_to_ca2[country_name.strip()]
    # par exemple 'EU'
    concode = country_alpha2_to_continent_code(calpha2)
    return int(concode == continent)


def changeDate(date_str: str):
    return datetime.strptime(date_str, "%m/%d, %H:%M").strftime("2021-%m-%d")


def loadTrips():
    """ Charge les voyages des navires depuis le fichier 'voyages.csv'
    et ajoute les variables binaires pour les continents de départs et d'arrivées

    Returns
    -------
    DataFrame
        Dataframe contenant les voyages
    """

    df_trips = pd.read_csv('./Data/Portcalls/voyages.csv')
    # On ajoute des colonnes avec les codes des pays de départ et d'arrivée
    for continent in continents:
        df_trips[f'D_{continent}'] = df_trips['Dcountry'].apply(isInContinent, args=(continent,))
        df_trips[f'A_{continent}'] = df_trips['Acountry'].apply(isInContinent, args=(continent,))
    # On modifie l'écriture des dates de départ et d'arrivées pour matcher celle des prix Europe
    df_trips['Dtime'] = df_trips['Dtime'].apply(changeDate)
    df_trips['Atime'] = df_trips['Atime'].apply(changeDate)
    return df_trips


def findNearestDate(date_str: str, df_price: pd.DataFrame, delta: int):
    """ Trouve la date la plus proche décalée de delta jours dans l'index d'un dataframe.

    Paramètres
    ----------
    date_str : str
        La date à trouver
    df_price : pandas.Dataframe
        Le dataframe dont l'index doit contenir des dates sous un format texte
    delta : int
        décalage de la date à trouver. Si delta est positif, la date sera plus grande,
        sera plus avancée dans le temps

    Retours
    -------
    nearest_date : str
        Date la plus proche de celle recherchée qui est contenue dans l'index du dataframe

    Exemples
    -------
    >>> findNearestDate('2021-05-11', df, 3)
    2021-05-14  # si cette date est contenue dans l'index
    """
    # Dates du dataframe sous forme de liste
    list_dates = pd.to_datetime(df_price.index).values
    # On calcule la date la plus proche en valeur absolue
    pivot = np.datetime64(pd.to_datetime(date_str) + timedelta(days=delta))
    nearest_date = min(list_dates, key=lambda x: abs(x - pivot))
    # On la transforme en str dans le même format que dans le dataframe df_price
    return np.datetime_as_string(nearest_date, unit='D')


def loadSpotEur(df_global: pd.DataFrame, date='Dtime', delta=0):
    """ Ajoute le prix spot de l'Europe à la date 'date'
    décalées de 'delta'.

    Paramètres
    ----------
    df_global : pandas.Dataframe
        Le dataframe auquel rajouter la colonne des prix
    date : str
        Date de départ (Dtime) ou d'arrivée (Atime) du navire
    delta : int
        décalage de la date 'date'. Si delta est positif, la date sera plus grande,
        sera plus avancée dans le temps
    """
    # date doit être Dtime ou Atime
    if date not in ['Dtime', 'Atime']:
        date = 'Dtime'
    # On charge les prix spots de l'Europe
    df_eur_price = pd.read_csv('./Data/SpotEur.csv', index_col='Date')
    # On ajoute la colonne
    df_global[f'Eur_Spot_{delta}'] = df_global[date].apply(
            lambda x: df_eur_price.loc[findNearestDate(x, df_eur_price, delta), 'Prix'])


def loadSpotUS(df_global: pd.DataFrame, date='Dtime', delta=0):
    """ Ajoute le prix spot des USA à la date 'date'
    décalées de 'delta'.

    Paramètres
    ----------
    df_global : pandas.Dataframe
        Le dataframe auquel rajouter la colonne des prix
    date : str
        Date de départ (Dtime) ou d'arrivée (Atime) du navire
    delta : int
        décalage de la date 'date'. Si delta est positif, la date sera plus grande,
        sera plus avancée dans le temps
    """
    if date not in ['Dtime', 'Atime']:
        date = 'Dtime'
    df_us_spot = pd.read_csv('./Data/SpotUS.csv', index_col='Date')
    df_global[f'US_Spot_{delta}'] = df_global[date].apply(
        lambda x: df_us_spot.loc[findNearestDate(x, df_us_spot, delta), 'Prix US'])


def mergeAsiaFutures(list_date: list, delta: int, df_price: pd.DataFrame):
    """ Transforme la liste de date en liste de prix grâce au dataframe

    Paramètres
    ----------
    list_date : list
        La liste des dates auxquelles il faut relier le prix de df_price
    delta : int
        décalage de la date 'date'. Si delta est positif, la date sera plus grande,
        sera plus avancée dans le temps
    df_price : pandas.dataframe
        Dataframe dont l'index est formé des dates et qui contient une colonne de prix

    Retours
    ----------
    list_price : list
        Liste des prix correspondant aux dates
    """
    list_price = []
    for date in list_date:
        # On souhaite renvoyer le mois suivant la date du prix
        # Ex: prix le 3 février -> on renvoie le prix de mars
        up_date = findNearestDate(date, df_price, delta)
        # On réduit le df pour ne garder que les prix mis à jour le up_date
        df = df_price.loc[up_date]
        # On prend le mois suivant up_date
        dt_month = (datetime.strptime(up_date, "%Y-%m-%d") + timedelta(days=31))
        str_month = dt_month.strftime("%Y-%m")
        # On renvoie la valeur associé au mois
        if not df[df['Month'] == str_month].empty:
            list_price.append(df[df['Month'] == str_month]['Prior Settle'].values[0])
        else:
            list_price.append(np.nan)
    return list_price


def loadFutures(df_global: pd.DataFrame, name: str, date='Dtime', delta=0):
    """ Charge les futures de la région 'name' dans le dataframe 'global'

    Paramètres
    ----------
    df_global : pandas.Dataframe
        Le dataframe auquel rajouter la colonne des prix
    name : str
        Nom de la région : Eur ou Asia
    date : str
        Date de départ (Dtime) ou d'arrivée (Atime) du navire
    delta : int
        décalage de la date 'date'. Si delta est positif, la date sera plus grande,
        sera plus avancée dans le temps

    Retours
    ----------
    list_price : list
        Liste des prix correspondant aux dates
    """
    if name == 'Asia':
        mergeFunc = mergeAsiaFutures
        fut_path = './Data/FuturesAsie.csv'
        index_col = 'Update date (CT)'
    elif name == 'Eur':
        mergeFunc = mergeEurFutures
        fut_path = './Data/FuturesEur.csv'
        index_col = 'Trading Day'

    if date not in ['Dtime', 'Atime']:
        date = 'Dtime'

    df_fut = pd.read_csv(fut_path, index_col=index_col)
    list_date = df_global[date].values
    list_fut = mergeFunc(list_date, delta, df_fut)
    df_fut = pd.DataFrame(list_fut, columns=[f'{name}_Fut_{delta}'])
    return pd.concat([df_global, df_fut], axis=1)


def mergeEurFutures(list_date, delta, df_price):
    """ Transforme la liste de date en liste de prix grâce au dataframe

    Paramètres
    ----------
    list_date : list
        La liste des dates auxquelles il faut relier le prix de df_price
    delta : int
        décalage de la date 'date'. Si delta est positif, la date sera plus grande,
        sera plus avancée dans le temps
    df_price : pandas.dataframe
        Dataframe dont l'index est formé des dates et qui contient une colonne de prix

    Retours
    ----------
    list_price : list
        Liste des prix correspondant aux dates
    """
    list_price = []
    for date in list_date:
        # On souhaite renvoyer le mois suivant la date du prix
        # Ex: prix le 3 février -> on renvoie le prix de mars
        up_date = findNearestDate(date, df_price, delta)
        list_price.append(df_price.loc[up_date, 'Month+1'])
    return list_price


def loadFuturesEur(df_global: pd.DataFrame, date='Dtime', delta=0):
    return loadFutures(df_global=df_global, date=date, delta=delta, name='Eur')


def loadFuturesAsia(df_global: pd.DataFrame, date='Dtime', delta=0):
    return loadFutures(df_global=df_global, date=date, delta=delta, name='Asia')


basic_param = {
    'SpotEur': True,
    'Delta_SE': [0],
    'Date_SE': 'Dtime',

    'SpotUS': False,
    'Delta_SU': [0],
    'Date_SU': 'Dtime',

    'FuturesAsia': True,
    'Delta_FA': [0, -5],
    'Date_FA': 'Dtime',

    'FuturesEur': True,
    'Delta_FE': [0, -5, 3],
    'Date_FE': 'Dtime',

    'Save': True,
    'Return': False,
}


def loadAll(param=basic_param):
    """ Charge toutes les colonnes selon les paramètres

    Paramètres
    ----------
    param : set
        dictionnaire des paramètres

    Retours
    ----------
    df_global : pandas.dataframe
        si Return == True renvoie le dataframe complet
    """
    t1 = time()

    df_global = loadTrips()
    print("Voyages")

    if param['SpotEur']:
        date, delta = param['Date_SE'], param['Delta_SE']
        for delt in delta:
            loadSpotEur(df_global, date, delt)
        print("Spot Europe")

    if param['SpotUS']:
        date, delta = param['Date_SU'], param['Delta_SU']
        for delt in delta:
            loadSpotUS(df_global, date, delt)
        print("Spot US")

    if param['FuturesAsia']:
        date, delta = param['Date_FA'], param['Delta_FA']
        for delt in delta:
            df_global = loadFuturesAsia(df_global, date, delt)
        print("Futures Asie")

    if param['FuturesEur']:
        date, delta = param['Date_FE'], param['Delta_FE']
        for delt in delta:
            df_global = loadFuturesEur(df_global, date, delt)
        print("futures Europe")

    t2 = time()
    print(f"Fini en {round(t2-t1,1)} secondes")
    if param['Save']:
        df_global.to_csv('./Data/loadAll.csv')
    if param['Return']:
        return df_global


if __name__ == '__main__':
    df = loadAll()
