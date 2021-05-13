import requests   # requests.get
import json  # json.loads
from bs4 import BeautifulSoup as bs
from datetime import datetime  # datetime.datetime.strptime

# Importation du fichier html qui est sous format json
url = "https://www.powernext.com/table-feed/132743/153/17"
requete = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
jayson = json.loads(requete.content)
soupe = bs(jayson['html'], features='html.parser')

# Données déjà stockées pour récupérer la dernière date
with open('FuturesEur.csv', 'r') as file:
    LastDate = file.readlines()[-1].split(',')[0]
    LastDate = datetime.strptime(LastDate, '%Y-%m-%d')

# Traitement des données de la soupe
data = []  # Liste des données à ajouter (sous formes de string)

day_list = soupe.find('tbody').find_all('tr')
for day in day_list:
    # prices_list est la liste de toutes les données d'une journée
    prices_list = day.find_all('td')
    # On la convertit maintenant sous la forme d'une string
    prices_str = '\n'
    for price in prices_list[0:-1]:
        prices_str += (price.string + ',')
    prices_str += prices_list[-1].string
    date = datetime.strptime(prices_list[0].string, '%Y-%m-%d')
    if date > LastDate:
        # On n'a pas cette donnée donc on l'ajoutera
        data.append(prices_str)
    else:
        # On est arrivé aux données déjà stockées : il faut écrire data
        break

# Ecriture dans le fichier
if len(data):
    with open('FuturesEur.csv', 'a') as file:
        data.reverse()
        for elem in data:
            file.write(elem)
else:
    print("Pas de nouvelles données")
    print(f"Dernière date : {LastDate}")

# Récupération en-tête et mise en forme
""" entete = soupe.find('thead').find_all('th')
beau_entete = []
for item in entete:
    beau_entete.append(item.string)
print(beau_entete) """
