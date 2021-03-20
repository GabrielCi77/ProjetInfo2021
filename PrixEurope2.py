import requests
import json
from datetime import date, timedelta
#il faut le lancer en fin de journée pour que le prix soit marqué
#met à jour le fichier eurPrice.csv
url = "https://www.powernext.com/data-feed/132735/139/17" #EGSI TTF
requete = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})

all_data = json.loads(requete.content)
price = all_data['values'][0]['data'][-1]['y']
date_price = date.today() + timedelta(days=3)

with open('eurPrice.csv', 'a') as file:
    file.write('\n')
    file.write(f"{date_price},{price}")