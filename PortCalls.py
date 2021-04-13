"""
Create a csv with the last port calls of each boat (600~) named PortCalls-today.csv
You  need to have chromedriver.exe in the same folder as the script
The version of chromedriver depends on the version of chrome you are using
The script is using data.csv which is the list of every boat in activity
The script uses progressbar to show in the terminal the progression
It runs during ~30mins
"""

from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as Dwait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import csv
from progress.bar import Bar

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


def GetData2(url, driver):
    """
    Cette fonction prend en entrée une url de data ainsi que le driver pour
    acquérir les données des derniers port calls et les renvoyer sous la forme
    d'une liste
    """
    driver.get(url)
    try:
        Dwait(driver, 4).until( EC.presence_of_element_located((By.CLASS_NAME, "flx._rLk.t5UW5")) )
    except TimeoutException:
        print(f"Timeout no port calls, url: {url}")
        try:
            Dwait(driver, 2).until( EC.presence_of_element_located((By.ID, "port-calls")) )
        except Exception as e:
            print(f"error with {url} : {e}")
            data = []
        except:
            print(f"error with {url}")
            data = []
    finally:
        tableau = driver.find_elements_by_class_name('vfix-top')[3]
        data = tableau.text.split('\n')
    return data

def TraitData(data, imo):
    """
    Cette fonction traite les données de GetData pour écrire une seule string
    prête à être copié dans le csv et qui contient toutes les lignes d'un bateau
    """
    res = ''
    for i in range(len(data)):
        if data[i] == 'Arrival (UTC)':
            res = res + imo + ',' + data[i-1] + ',"' + data[i+1] + '","' + data[i+3] + '","' + data[i+5] + '"\n'
    return res

def AllBoat2(name):
    """
    Cette fonction définit le driver (et ouvre la fenêtre chrome)
    et parcourt les lignes de data pour lancer l'acquisition sur une page
    Elle copie ensuite les données traitées dans le csv final
    """
    driver = webdriver.Chrome(options=options)
    with open('data.csv') as f:
        taille = len(f.readlines())
    with open('data.csv', newline='') as csvfile:
        with open(name, 'a') as scraping:
            scraping.write('IMO, Port, Country, Arrival, Departure, In Port\n')
            bar = Bar('Processing', max=taille)
            content = csv.reader(csvfile)
            for row in content:
                if row[3] != 'Lien':
                    url = 'https://www.' + row[3]
                    imo = row[1]
                    data = GetData2(url, driver)
                    data = TraitData(data, imo)
                    scraping.write(data)
                    bar.next()
            bar.finish()

if __name__ == '__main__':
    today = date.today()
    AllBoat2(f'PortCalls-{today}.csv')


#D'autres fonctions qui ne sont plus utiles
""" def GetData(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)
    tableau = driver.find_elements_by_class_name('vfix-top')[3]
    data = tableau.text
    driver.quit()
    data = data.split('\n')
    return data """

""" def AllBoat():
    df = pd.DataFrame(columns=['IMO', 'Port', 'Arrival', 'Departure', 'In Port'])
    with open('data2.csv') as f:
        taille = len(f.readlines())
    
    with open('data2.csv', newline='') as csvfile:
        bar = Bar('Processing', max=taille)
        content = csv.reader(csvfile)
        for row in content:
            if row[3] != 'Lien':
                url = 'https://www.' + row[3]
                imo = row[1]
                data = GetData(url)
                df = ListI(data, df, imo)
                bar.next()
        bar.finish()
    return df """

""" def ListI(data, df, imo):
    for i in range(len(data)):
        if data[i] == 'Arrival (UTC)':
            df = df.append({'IMO' : imo,
                            'Port' : data[i-1],
                            'Arrival' : data[i+1],
                            'Departure' : data[i+3] ,
                            'In Port' : data[i+5]},
                            ignore_index = True)
    return df """