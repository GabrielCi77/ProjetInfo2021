from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import pandas as pd
from sklearn.linear_model import LinearRegression as LR
from datetime import datetime
import matplotlib.pyplot as plt

# Passe des codes des continents à leur zone géographique (-1, 0, 1)
# Les zones sont très larges : faut il supprimer certains pays de l'étude ?
# Ici Qatar est dans l'Europe alors que ce n'est pas le cas
# on peut imaginer 0=Europe // 1=Asie // 2=producteur // 3=Hors-étude ?
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


df_trips = pd.read_csv('../Data/Portcalls/voyages.csv')
# On ajoute des colonnes avec les codes des pays de départ et d'arrivée
for continent in price_of_country.keys():
    df_trips[f'D_{continent}'] = df_trips['Dcountry'].apply(convertNameToCode, args=(continent,))
    df_trips[f'A_{continent}'] = df_trips['Acountry'].apply(convertNameToCode, args=(continent,))

# On sélectionne les voyages depuis l'Amérique vers l'Europe ou l'Asie
df_filter = df_trips[(df_trips['D_NA'] == 1) & (df_trips['A_EU'] + df_trips['A_AS'] == 1)]
df_filter = df_filter.drop(columns=['IMO', 'Dport', 'Dcountry', 'Aport', 'Acountry'])

# On charge les prix spots de l'Europe
df_eur_price = pd.read_csv('../Data/SpotEur.csv', index_col='Date')


def changeDate(date_str):
    return datetime.strptime(date_str, "%m/%d, %H:%M").strftime("2021-%m-%d")


# On modifie l'écriture des dates de départ et d'arrivées pour matcher celle des prix Europe
df_filter['Dtime'] = df_filter['Dtime'].apply(changeDate)
df_filter['Atime'] = df_filter['Atime'].apply(changeDate)

# On ajoute les prix de l'Europe quand le bateau arrive et on normalise
df_filter['Eur_Price'] = df_filter['Dtime'].apply(lambda x: df_eur_price.loc[x, 'Prix'])
max_price = df_filter['Eur_Price'].max()
df_filter['Eur_Price'] = df_filter['Eur_Price'].apply(lambda x: x/max_price)
print(df_filter.head)

# X correspond aux valeurs d'entrée et y à la valeur de sortie selon X
X = df_filter[['Eur_Price']].to_numpy()
y = df_filter[['A_EU']].to_numpy()

# On sépare en deux sets
size = int(0.2*len(X))
X_train = X[0:-size]
y_train = y[0:-size]

X_test = X[-size:]
y_test = y[-size:]

# On entraine une régression linéaire
print(len(X_train), len(y_train))
reg = LR().fit(X_train, y_train)
y_pred = reg.predict(X_test)

# Plot outputs
plt.scatter(X_test, y_test,  color='black')
plt.plot(X_test, y_pred, color='blue', linewidth=3)
plt.yticks([0,1], ['Asie', 'Europe'])
plt.xlabel("Prix Spot Europe du jour d'arrivée du bateau")
plt.show()

# 44% de la production part vers l'Europe en moyenne sans aucune réflexion sur les prix, les dates, etc
# On peut ajouter les dates mais il faut les convertir en float
# il serait intéressant de connaître la durée entre l'achat d'une quantité de GNL dans un pays jusqu'à sa vente dans un autre pour utiliser
# les prix correspondants
