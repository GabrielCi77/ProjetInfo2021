import csv
import pandas as pd
'''
Commentaires E-CUBE (Marwane) : 

- Commentaires généraux :
    - Structurer le dossier en sous-dossiers contenant des fichiers de nature distincte. Typiquement :
        - data : contient toutes les données, dont celles qui sont scrapées
        - lib : contient tous les scripts Python
    - Renommer les scripts suivant une nomenclature facile à comprendre, avec une numérotation alphanumérique pour comprendre
    dans quel ordre ils sont/doivent être run
        - Ex : tous les Futures peuvent être dans un même bloc A1, et seraient nommés A11_FuturesEur, A12_FuturesAsie par exemple
    - Mettre les fonctions dans des scripts dédiées, et les appeler depuis des scripts main (ne pas mélanger fonctions et run des fonctions
    dans un même script)

- Commentaires spécifiques à ce script : 
    - Que fait ce script ?
    - Les lignes 14 à 26 peuvent facilement être écrites de manière stable en 3 lignes (voir code ajouté)
        - Pourquoi définir des noms tronqués dans dict_month si vous ne prenez que les 3 premières lettres de string (l.41) ?
        Autant définir directement les noms complets dans dict_month :)
    - Au lieu d'utiliser les fonctions open et csv_reader/csv_writer, utiliser read_csv et write_csv de la librairie pandas
    - Les noms des CSV que vous ouvrez/fermez changent-ils à chaque fois que vous lancez le script ? Si oui, il y a un enjeu à 
    variabiliser le nom du fichier
'''


### Ajout Marwane ###
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_numbers = ["%.2d" % i for i in range(1, len(months)+1)]
dict_month = {months[i]: month_numbers[i] for i in range(len(months))}
###
dict_month = {}
dict_month['Jan']= '01'
dict_month['Feb']= '02'
dict_month['Mar']= '03'
dict_month['Apr']= '04'
dict_month['May']= '05'
dict_month['Jun']= '06'
dict_month['Jul']= '07'
dict_month['Aug']= '08'
dict_month['Sep']= '09'
dict_month['Oct']= '10'
dict_month['Nov']= '11'
dict_month['Dec']= '12'

def convertdate(string):
    # print(string)
    if string[0] == '-':
        return '-'
    convmonth = dict_month[string[:3]]
    i = 0
    ind = 0
    for car in string :
        if car == ',':
            ind = i
        i+=1
    convday = string[4:ind]
    if len(convday)==1:
        convday = '0'+convday
    convhour = string[ind+2:ind+7]
    return f'2021-{convmonth}-{convday}-{convhour}'
 
fichier = open('../Data/donnees-navires/list-vessels-2021-04-30-old.csv','r')
fichiercsv = csv.reader(fichier, delimiter=',')
out = open("../Data/donnees-navires/list-vessels-2021-04-30.csv", "w", newline='')
outw = csv.writer(out)
listecsv = []
i = 0
for ligne in fichiercsv:
    if i > 0 :
        ligne[9] = convertdate(ligne[9])
        ligne[12] = convertdate(ligne[12])
    listecsv.append(ligne)
    i =+ 1
outw.writerows(listecsv)
out.close()
fichier.close()