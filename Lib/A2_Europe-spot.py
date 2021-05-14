# Cherche et stocke dans le fichier SpotEur.csv les prix Spots de l'Europe

import requests
import json
import datetime

# Importation du fichier json contenant les prix EGSI de la place de marché TTF
url = "https://www.powernext.com/data-feed/132735/139/17"
request = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
all_data = json.loads(request.content)

# On regarde quelle est la dernière date déjà enregistré dans le csv
with open('SpotEur.csv', 'r') as file:
    last_date = file.readlines()[-1].split(',')[0]  # si on a un week-end la dernière date est forcément le dimanche
    last_date = datetime.datetime.strptime(last_date, '%Y-%m-%d')


def updateDateAndPrice(i):
    # On attribue les valeurs du json à nos variables
    price = all_data['values'][0]['data'][-i]['y']
    price_date = all_data['values'][0]['data'][-i]['name'][3:]   # WE 2021-03-22/23
    type = all_data['values'][0]['data'][-i]['name'][:2]
    # N'est utile que si type == 'WE'
    saturday = None

    if type == 'WE':  # price_date : WE 2021-03-21/22
        saturday = price_date[0:10]
        price_date = price_date[0:8] + price_date[11:13]  # on se place sur le dimanche
    # On convertit la date dans un format qui permet de les comparer
    price_date = datetime.datetime.strptime(price_date, '%Y-%m-%d')
    return price_date, saturday, price, type


# Première itération des prix : on stocke la dernière valeur du site
price_date, saturday, price, type = updateDateAndPrice(1)
diff_date = price_date - last_date

# Itération jusqu'à la valeur enregistrée dans le fichier
data = []
i = 2
while last_date < price_date:
    """On ajoute à la liste data la ligne correspondant à une ou deux journées
    selon que la donnée de prix correspondent à un week-end ou un jour de semaine
    Le week end price_date s'écrit : WE 2021-03-21/22"""
    if type == 'WE':
        data.append('\n' + price_date.strftime('%Y-%m-%d') + ',' + str(price))
        data.append('\n' + saturday + ',' + str(price))
    elif type == 'DA':
        data.append('\n' + price_date.strftime('%Y-%m-%d') + ',' + str(price))

    # On met à jour les variables
    price_date, saturday, price, type = updateDateAndPrice(i)

    # Mise à jour de l'itérateur
    if type == 'WE':
        i += 2  # On a stocké samedi et dimanche donc on saute une étape
    else:
        i += 1

# Ecriture dans le fichier
if diff_date != datetime.timedelta(0, 0, 0):
    with open('SpotEur.csv', 'a') as file:
        # Il faut inverser la liste pour conserver l'ordre chronologique
        # avant de pouvoir écrire dans le fichier
        data.reverse()
        for elem in data:
            file.write(elem)
    # Interaction dans le terminal
    print(f"{diff_date} ont (a) été ajouté(s) :")
    print(f"de {last_date} \nà  {last_date + diff_date}")
else:
    print("Pas de nouvelle valeur")
    print(f"dernière date : {last_date}")
