# Cherche et stocke dans le fichier FuturesAsie.csv les prix Futures de l'Asie

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as Dwait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime


"""TOUTES LES OPTIONS UTILES POUR CHROMEDRIVER"""
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# AGRESSIVE: options.setPageLoadStrategy(PageLoadStrategy.NONE)
# https://www.skptricks.com/2018/08/timed-out-receiving-message-from-renderer-selenium.html
options.add_argument("start-maximized")  # https://stackoverflow.com/a/26283818/1689770
options.add_argument("enable-automation")  # https://stackoverflow.com/a/43840128/1689770
# options.add_argument("--headless")
# only if you are ACTUALLY running headless
options.add_argument("--no-sandbox")  # https://stackoverflow.com/a/50725918/1689770
options.add_argument("--disable-infobars")  # https://stackoverflow.com/a/43840128/1689770
options.add_argument("--disable-dev-shm-usage")  # https://stackoverflow.com/a/50725918/1689770
options.add_argument("--disable-browser-side-navigation")  # https://stackoverflow.com/a/49123152/1689770
options.add_argument("--disable-gpu")  # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc


def changeDateOfMonth(x: str):
    """Change le format de la date du mois

    Paramètres
    ----------
    x : string

    Retours
    -------
    x : string

    Exemples
    -------
    changeDateOfMonth('JUL 2021') -> '2021-07'"""

    try:
        return datetime.strptime(x, "%b %Y").strftime("%Y-%m")
    except ValueError:
        return x


def changeDateOfUpdate(x: str):
    """Change le format de la date de mise à jour :

    Paramètres
    ----------
    x : string

    Retours
    -------
    x : string

    Exemples
    -------
    changeDateOfMonth('6:00:00 CT\\r\\n13 Jun 2021') -> 2021-06-13"""

    try:
        return datetime.strptime(x, "%H:%M:%S CT\r\n%d %b %Y").strftime("%Y-%m-%d")
    except ValueError:
        return x


def extractInfos(list_data: list, row):
    """
    Permet d'ajouter les éléments d'une ligne du tableau à notre liste de données

    Paramètres
    ----------
    list_data : list
    row : WebElement
    """
    date = row.find_element_by_tag_name('span').text.split()  # date = ['AUG', '2021', 'JKMQ1']
    date = date[0] + ' ' + date[1] # date = AUG 2021
    price = row.find_elements_by_class_name('table-cell')[5].text
    update = row.find_elements_by_class_name('table-cell')[-1].text
    # On met à jour la liste de données
    list_data.append((changeDateOfMonth(date),
                      price,
                      changeDateOfUpdate(update)))


def getAndSaveAsiaFutures():
    # Connexion à la page des futures Asie par chromedriver pour charger les données du tableau des prix
    url_asia_price = 'https://www.cmegroup.com/trading/energy/natural-gas/lng-japan-korea-marker-platts-swap.html'
    driver = webdriver.Chrome(options=options)
    driver.get(url_asia_price)

    # Création de la liste qui contiendra toutes nos données
    list_data = []
    # On attend que la table soit chargé pour extraire les informations
    rows = Dwait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table-row-animate")))
    # Liste python de toutes les lignes du tableau du site web
    rows = driver.find_elements_by_class_name('table-row-animate')
    
    # On itère sur ces lignes pour transformer cette liste en liste de données
    for row in rows:
        extractInfos(list_data, row)
    driver.quit()

    # Stockage des informations dans le fichier FuturesAsie.csv
    df_columns = ['Month', 'Prior Settle', 'Update date (CT)']
    df_price = pd.DataFrame(data=list_data, columns=df_columns)
    df_price.to_csv('../data/FuturesAsie.csv', mode='a', header=False, index=False)

    # Suppression des doublons
    df_all_price = pd.read_csv('../data/FuturesAsie.csv')
    df_all_price = df_all_price.drop_duplicates()
    df_all_price.to_csv('../data/FuturesAsie.csv', header=True, index=False)


if __name__ == '__main__':
    getAndSaveAsiaFutures()
