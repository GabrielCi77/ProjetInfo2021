import requests
import json
import datetime
#il faut le lancer en fin de journée pour que le prix soit marqué
#met à jour le fichier eurPrice.csv

#Importation du fichier json web
url = "https://www.powernext.com/data-feed/132735/139/17" #EGSI TTF
requete = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
all_data = json.loads(requete.content)

#Données déjà stockées
with open('eurPrice.csv', 'r') as file:
        LastDate = file.readlines()[-1].split(',')[0] #si on a un week end la dernière date est forcément le dimanche
        LastDate = datetime.datetime.strptime(LastDate, '%Y-%m-%d')

#Première itération des prix
price = all_data['values'][0]['data'][-1]['y']
price_date = all_data['values'][0]['data'][-1]['name'][3:]   #WE 2021-03-22/23
type = all_data['values'][0]['data'][-1]['name'][:2]

if type == 'WE': #price_date : WE 2021-03-21/22
    samedi = price_date[0:10]
    price_date = price_date[0:8] + price_date[11:13] #on se place sur le dimanche
price_date = datetime.datetime.strptime(price_date, '%Y-%m-%d')

#Différence:
diff = price_date - LastDate

#Itération jusqu'à la dernière valeur stockée
data = []
i = 2
while LastDate < price_date:
    if type=='WE':
        data.append( '\n' + price_date.strftime('%Y-%m-%d') + ',' + str(price) )
        data.append( '\n' + samedi + ',' + str(price) )
    elif type == 'DA':
        data.append('\n' + price_date.strftime('%Y-%m-%d') + ',' + str(price) )

    price = all_data['values'][0]['data'][-i]['y']
    price_date = all_data['values'][0]['data'][-i]['name'][3:]
    type = all_data['values'][0]['data'][-i]['name'][:2] 

    if type == 'WE': #price_date : WE 2021-03-21/22
        samedi = price_date[0:10]
        price_date = price_date[0:8] + price_date[11:13] #on se place sur le dimanche
    price_date = datetime.datetime.strptime(price_date, '%Y-%m-%d')
    
    if type == 'WE':
        i+=2 #On a stocké samedi et dimanche donc on saute une étape
    else:
        i+=1

#Ecriture dans le fichier
if diff != datetime.timedelta(0,0,0):
    with open('eurPrice.csv', 'a') as file:
        data.reverse()
        for elem in data:
            file.write(elem)
    print(f"{diff} ont (a) été ajouté(s) :")
    print(f"de {LastDate} \nà  {LastDate + diff}")

else:
    print("Pas de nouvelle valeur")
    print(f"dernière date : {LastDate}")