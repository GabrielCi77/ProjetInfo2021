import csv
import pandas as pd

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
 
fichier = open('list-vessels-2021-04-30-old.csv','r')
fichiercsv = csv.reader(fichier, delimiter=',')
out = open("list-vessels-2021-04-30.csv", "w", newline='')
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