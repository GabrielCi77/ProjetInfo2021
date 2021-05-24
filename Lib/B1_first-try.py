from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import pandas as pd
from sklearn.linear_model import LinearRegression as LR
import numpy as np


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
df_trips = pd.read_csv('../Data/Portcalls/voyages.csv')
print(df_trips.head())


def convertNameToCode(country_name):
    try:
        # code a deux lettres du pays
        calpha2 = country_name_to_country_alpha2(country_name.strip())
    except KeyError:
        # Certains noms de pays de nos jeux de données ne respectent pas la norme dispo sur wikipedia
        # https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        # une solution est de les traiter par une suite de if en cas d'erreur mais il existe surement mieux
        # on peut aussi les données quand on les écrit
        if country_name.strip() == 'Korea':
            calpha2 = 'KR'  # South Korea
        elif country_name.strip() == 'United Arab Emirates (UAE)':
            calpha2 = 'AE'
        elif country_name.strip() == 'Trinidad & Tobago':
            calpha2 = 'TT'
        elif country_name.strip() == 'United States (USA)':
            calpha2 = 'US'
        elif country_name.strip() == 'United Kingdom (UK)':
            calpha2 = 'GB'
        elif country_name.strip() == "Cote d'Ivoire":
            calpha2 = 'CI'
        else:
            calpha2 = country_name
    # par exemple 'EU'
    concode = country_alpha2_to_continent_code(calpha2)
    # et donc 0 pour 'EU'
    code_name = continents[concode]
    return code_name


# On ajoute des colonnes avec les codes des pays de départ et d'arrivée
df_trips['Dcode'] = df_trips['Dcountry'].apply(convertNameToCode)
df_trips['Acode'] = df_trips['Acountry'].apply(convertNameToCode)
print(df_trips.head())

# On sélectionne les voyages depuis l'Amérique vers l'Europe ou l'Asie
df_filter = df_trips[df_trips['Dcode'] == -1]
df2 = df_filter[df_filter['Acode'] > -1]

# X correspond aux valeurs d'entrée et y à la valeur de sortie selon X
X = df2[['Dcode']].to_numpy()
y = df2[['Acode']].to_numpy()

# On entraine uen régression linéaire
reg = LR().fit(X, y)
print(reg.predict(np.array([-1]).reshape(1, -1)))

# 44% de la production part vers l'Europe en moyenne sans aucune réflexion sur les prix, les dates, etc
# On peut ajouter les dates mais il faut les convertir en float
# il serait intéressant de connaître la durée entre l'achat d'une quantité de GNL dans un pays jusqu'à sa vente dans un autre pour utiliser
# les prix correspondants
