import awoc
import pandas
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

coun2=countries[countries['Net GHG balance']!=0]
print(coun2)

import geopandas as gpd

shapefile = 'Data/countries_110m/ne_110m_admin_0_countries.shp'
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']
merged = gdf.merge(countries, left_on = 'country_code', right_on = 'code')
merged.to_csv("./test.csv")        
import json
#Read data to json.
merged_json = json.loads(merged.to_json())
#Convert to String like object.
json_data = json.dumps(merged_json)

from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data)
#Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40)
#Define custom tick labels for color bar.
tick_labels = {'-40000': '<-30000kg', '-10000': '10000kg', '-5000':'-5000kg', '-2000':'-2000kg', '-1000':'1000', '0':'0', '1000':'1000kg','2000':'2000kg', '4000': '4000kg','6000':'6000kg'}
#Create color bar. 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
#Create figure object.
p = figure(title = 'Weight of CO2 displaced by LNG tankers', plot_height = 600 , plot_width = 950, toolbar_location = None)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource,fill_color = {'field' :'kilogram_CO2', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify figure layout.
p.add_layout(color_bar, 'below')
#Display figure inline in Jupyter Notebook.
output_file()
#Display figure.
show(p)