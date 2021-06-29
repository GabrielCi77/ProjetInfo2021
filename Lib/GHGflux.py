import awoc
from bokeh.models.mappers import LogColorMapper
import pandas as pd
import numpy as np 
from csv import reader
import scipy.special
import pyproj

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

countries = pd.DataFrame(0.0,columns=['Net GHG balance'],index=countries_list)
countries['Productor']=False
countries = countries.astype({"Net GHG balance": float})

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

boatList = pd.read_csv("./Data/donnees-navires/list-vessels-2021-06-01.csv",index_col=1)
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

coun2=countries[countries['Net GHG balance']!=0]
coun2=coun2.astype({"Net GHG balance":float})
print(coun2)

import geopandas as gpd
def changecountry (a):
    if a=='South Korea':
        a='Korea'
    if a=='United Arab Emirates':
        a='United Arab Emirates (UAE)'
    if a=='Trinidad and Tobago':   
        a='Trinidad & Tobago'
    if a=='United States of America':
        a='United States (USA)'
    if a=='United Kingdom':
        a='United Kingdom (UK)'
    if a=="Ivory Coast":
        a="Cote d'Ivoire"
    if a=="United Republic of Tanzania":
        a="Tanzania"
    return a

def change (a):
    return -a

shapefile = 'Data/countries_110m/ne_110m_admin_0_countries.shp'
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns
gdf.columns = ['country', 'country_code', 'geometry']
gdf['country']=gdf['country'].apply(changecountry)
merged = gdf.merge(countries, left_on = 'country', right_index=True)
merged=merged.astype({"Net GHG balance":float})
import json
#Read data to json.
mg1=merged[merged['Net GHG balance']>0]
mg2=merged[merged['Net GHG balance']<0]
mg3=merged[merged['Net GHG balance']==0]
mg2['Net GHG balance']=mg2['Net GHG balance'].apply(change)
merged_json1 = json.loads(mg1.to_json())
merged_json2 = json.loads(mg2.to_json())
merged_json3 = json.loads(mg3.to_json())

#Convert to String like object.
json_data1 = json.dumps(merged_json1)
json_data2 = json.dumps(merged_json2)
json_data3 = json.dumps(merged_json3)

from bokeh.io import export, show,export_png
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
#Input GeoJSON source that contains features for plotting.
geosource1 = GeoJSONDataSource(geojson = json_data1)
geosource2 = GeoJSONDataSource(geojson = json_data2)
geosource3 = GeoJSONDataSource(geojson = json_data3)

#Define a sequential multi-hue color palette.
palette1 = brewer['BuGn'][8]
palette2 = brewer['YlOrBr'][8]
#Reverse color order so that dark blue is highest obesity.
palette1=palette1[::-1]
palette2=palette2[::-1]

max1=mg1['Net GHG balance'].max()
max2=mg2['Net GHG balance'].max()
min1=mg1['Net GHG balance'].min()
min2=mg2['Net GHG balance'].min()

#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper1 = LogColorMapper(palette = palette1, low = min1, high = max1)
color_mapper2 = LogColorMapper(palette = palette2, low = min2, high = max2)

#Define custom tick labels for color bar.
tick_labels1 = {str(min1): str(min1), '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', str(max1):  str(max1)}
tick_labels2 = {str(min2): str(min2), '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', str(max2):  str(max2)}

#Create color bar. 
color_bar1 = ColorBar(color_mapper=color_mapper1, label_standoff=8,width = 500, height = 20,
border_line_color=None,location = (0,0), orientation = 'horizontal')
color_bar2 = ColorBar(color_mapper=color_mapper2, label_standoff=8,width = 500, height = 20,
border_line_color=None,location = (0,0), orientation = 'horizontal')

#Create figure object.
p = figure(title = 'Weight of CO2 displaced by LNG tankers', plot_height = 600 , plot_width = 950, toolbar_location = None)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource1,fill_color = {'field' :'Net GHG balance', 'transform' : color_mapper1},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
p.patches('xs','ys', source = geosource2,fill_color = {'field' :'Net GHG balance', 'transform' : color_mapper2},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
p.patches('xs','ys', source = geosource3,fill_color='white',
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

#Specify figure layout.
p.add_layout(color_bar1, 'below')
p.add_layout(color_bar2, 'below')

#Display figure.
export_png(p, filename='../figure/GHGflux.png')
show(p)