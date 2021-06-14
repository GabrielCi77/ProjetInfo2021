import awoc
import pandas
import numpy as np 
from csv import reader
import scipy.special

world = awoc.AWOC()

countries_list = world.get_countries_list() ## Crée une liste de tout les pays
for i in range(len(countries_list)):
    if countries_list[i]=='South Korea':
        countries_list[i]='Korea'
    if countries_list[i]=='United Arab Emirates':
        countries_list[i]='United Arab Emirates (UAE)'
    if countries_list[i]=='Trinidad and Tobago':   
        countries_list[i]='Trinidad & Tobago'
    if countries_list[i]=='United States':
        countries_list[i]='United States (USA)'
    if countries_list[i]=='United Kingdom':
        countries_list[i]='United Kingdom (UK)'
    if countries_list[i]=="Ivory Coast":
        countries_list[i]="Cote d'Ivoire"

countries = pandas.DataFrame(0,columns=['Net GHG balance'],index=countries_list)
countries['Productor']=False


prod=['United States (USA)',
        'Canada',
        'Norway',
        'Russia',
        'Algeria',
        'Nigeria',
        'Mozambique',
        'Qatar',
        'Indonesia',
        'Oman']

for l in prod:
        countries.loc[l,'Productor']=True

prodNB = {'United States (USA)': 0.48,
        'Canada': 0.15 ,
        'Norway':0.21,
        'Russia':0.3,
        'Algeria':0.3,
        'Nigeria':0.33,
        'Mozambique':0.3,
        'Qatar':0.39,
        'Indonesia':0.3,
        'Oman':0.28}

boatList = pandas.read_csv("./Data/donnees-navires/list-vessels-2021-06-01.csv",index_col=1)
boatList.loc[7390181,'GT']=0                  
with open('./Data/PortCalls/voyages.csv', 'r') as csv_file:
    csv_reader = reader(csv_file)
    # Passing the cav_reader object to list() to get a list of lists
    voyages = list(csv_reader)
    voyages=np.array(voyages)
    b=voyages[1,0]
    nbT=0
    for i in range (2,len(voyages)):
            if b==voyages[i,0]:
                nbT+=1
                if nbT>0:
                    exp=voyages[i-1,2][1:]
                    if exp=='Martinique':
                        exp='France'
                    imp=voyages[i,2][1:]
                    if imp=='Martinique':
                        imp='France'
                    if countries.loc[exp,'Productor']==True:
                       try:
                            V=boatList.loc[b,'GT']
                       except:
                            V=300
                       V=50*2.302*V/scipy.special.lambertw(500000000000*2.302*V) #Obtention du volume réel du bateau méthanier à partir du GT
                       P=0.42262*V
                       cg=prodNB[exp]*P
                       countries.loc[exp,'Net GHG balance']-=cg
                       countries.loc[imp,'Net GHG balance']+=cg
            else:
                b=voyages[i,0]
                nbT=0

count2=countries[countries['Net GHG balance'] != 0]
print(count2)
        

        


