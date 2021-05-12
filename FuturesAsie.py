from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as Dwait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd

'''
Commentaires E-CUBE (Marwane) : 
- Commenter les grandes étapes du code (toutes les deux ou trois lignes)
- Eviter d'entrer en dur plusieurs fois les mêmes choses (ex. : 'Month', 'Prior Settle' et 'Update date' en l.38 et 46)
- Un dataframe n'est pas fait pour grossir au fur et à mesure (ajout ligne par ligne avec append) : c'est non-optimisé et 
 chronophage. Je suggère plutôt de créer autant de dataframes que d'éléments dans "lignes", puis de les concaténer d'un coup
 avec pd.concat([liste de tous les dataframes]). 
'''

###########################

"""TOUTES LES OPTIONS UTILES POUR CHROMEDRIVER"""
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
#ChromeDriver is just AWFUL because every version or two it breaks unless you pass cryptic arguments
#AGRESSIVE: options.setPageLoadStrategy(PageLoadStrategy.NONE) #https://www.skptricks.com/2018/08/timed-out-receiving-message-from-renderer-selenium.html
options.add_argument("start-maximized") #https://stackoverflow.com/a/26283818/1689770
options.add_argument("enable-automation") #https://stackoverflow.com/a/43840128/1689770
#options.add_argument("--headless") #only if you are ACTUALLY running headless
options.add_argument("--no-sandbox") #https://stackoverflow.com/a/50725918/1689770
options.add_argument("--disable-infobars") #https://stackoverflow.com/a/43840128/1689770
options.add_argument("--disable-dev-shm-usage") #https://stackoverflow.com/a/50725918/1689770
options.add_argument("--disable-browser-side-navigation") #https://stackoverflow.com/a/49123152/1689770
options.add_argument("--disable-gpu") #https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc

url = 'https://www.cmegroup.com/trading/energy/natural-gas/lng-japan-korea-marker-platts-swap.html'
driver = webdriver.Chrome(options=options)
driver.get(url)
table = Dwait(driver, 10).until( EC.presence_of_element_located((By.ID, "quotesFuturesProductTable1")) )
body = table.find_element_by_tag_name('tbody')
lignes = body.find_elements_by_tag_name('tr')
df = pd.DataFrame(columns=['Month', 'Prior Settle', 'Update date (CT)'])
for tr in lignes:
    liste = tr.find_elements_by_tag_name('td')
    month = liste[0].text
    price = liste[4].text
    update_date = liste[-1].text
    #On peut modifier la date/ne pas la marquer peut-être

    df = df.append({'Month' : month,
                    'Prior Settle' : price,
                    'Update date (CT)' : update_date},
                    ignore_index=True)

driver.quit()
df.to_csv('FuturesAsie.csv', mode='a', header=False, index=False)