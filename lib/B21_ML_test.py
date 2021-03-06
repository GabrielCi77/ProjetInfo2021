import numpy as np
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import pandas as pd
from sklearn import model_selection
from sklearn import neighbors
from sklearn import preprocessing
from sklearn import metrics
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import plot_precision_recall_curve


# Tous les pays producteurs de GNL
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
continents = {
    'NA': -1,  # North America
    'SA': -1,  # South America
    'AS': 1,  # Asia
    'OC': 1,  # Australia
    'AF': 0,  # Africa
    'EU': 0,  # Europe
}

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
    df_trips = pd.read_csv('../Data/Portcalls/voyages.csv')
    # On ajoute des colonnes avec les codes des pays de départ et d'arrivée
    for continent in price_of_country.keys():
        df_trips[f'D_{continent}'] = df_trips['Dcountry'].apply(convertNameToCode, args=(continent,))
        df_trips[f'A_{continent}'] = df_trips['Acountry'].apply(convertNameToCode, args=(continent,))
    # On modifie l'écriture des dates de départ et d'arrivées pour matcher celle des prix Europe
    df_trips['Dtime'] = df_trips['Dtime'].apply(changeDate)
    df_trips['Atime'] = df_trips['Atime'].apply(changeDate)

    # On charge les prix spots de l'Europe
    df_eur_price = pd.read_csv('../Data/SpotEur.csv', index_col='Date')
    # On ajoute les prix de l'Europe quand le bateau arrive et on normalise
    df_trips['Eur_Price'] = df_trips['Dtime'].apply(lambda x: df_eur_price.loc[x, 'Prix'])
    max_price_eur = df_trips['Eur_Price'].max()
    df_trips['Eur_Price'] = df_trips['Eur_Price'].apply(lambda x: x/max_price_eur)

    # On charge les prix spot des US
    df_us_spot = pd.read_csv('../Data/SpotUS.csv', index_col='Date')
    df_trips['US_Price'] = df_trips['Dtime'].apply(mergeUSPrice, args=(df_us_spot,))
    max_price_us = df_trips['Eur_Price'].max()
    df_trips['US_Price'] = df_trips['US_Price'].apply(lambda x: x/max_price_us)
    return df_trips


def mergeUSPrice(date_str, df_price):
    i = 0
    while date_str not in df_price.index.values:
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
    return df_price.loc[date_str, 'Prix US']



def trainAndPlot(df_data):
    # On enlève les colonnes non utilisées pour le machine learning
    df_data = df_data.drop(columns=['Dcountry', 'Dtime', 'Atime', 'A_SA', 'D_SA', 'A_AF', 'D_AF', 'D_OC', 'A_OC', 'A_NA', 'A_AS'])
    
    X = np.array(df_data.drop(columns=['A_EU']))
    y = np.array(df_data['A_EU'])

    # On sépare en deux jeux de données
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, 
                                                                    test_size=0.20, 
                                                                    random_state=27)

    standard_scaler = preprocessing.StandardScaler()
    standard_scaler.fit(X_train)
    X_train = standard_scaler.transform(X_train)
    X_test = standard_scaler.transform(X_test)

    random_state = np.random.RandomState(0)

    predictor = svm.LinearSVC(random_state=random_state)
    predictor.fit(X_train, y_train)

    y_score = predictor.decision_function(X_test)
    average_precision = average_precision_score(y_test, y_score)

    print('Average precision-recall score: {0:0.2f}'.format(
      average_precision))

    disp = plot_precision_recall_curve(predictor, X_test, y_test)
    disp.ax_.set_title('2-class Precision-Recall curve: '
                   'AP={0:0.2f}'.format(average_precision))

if __name__ == '__main__':
    df_trips = loadTripsAndPriceData()
    df_trips = df_trips[(df_trips['A_EU'] + df_trips['A_NA'] == 1)]
    df_trips = df_trips.drop(columns=['IMO', 'Dport', 'Aport', 'Acountry'])
    trainAndPlot(df_trips)