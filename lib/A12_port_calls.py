"""
Create a csv with the last port calls of each boat (600~) named PortCalls-today.csv
You  need to have chromedriver.exe in the same folder as the script
The version of chromedriver depends on the version of chrome you are using
The script is using data.csv which is the list of every boat in activity
The script uses progressbar to show in the terminal the progression
It runs during ~30mins
"""

from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as Dwait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
import csv
from progress.bar import Bar
import pandas as pd
import numpy as np

"""TOUTES LES OPTIONS UTILES POUR CHROMEDRIVER"""
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# ChromeDriver is just AWFUL because every version or two it breaks unless you pass cryptic arguments
# AGRESSIVE: options.setPageLoadStrategy(PageLoadStrategy.NONE)
# https://www.skptricks.com/2018/08/timed-out-receiving-message-from-renderer-selenium.html
options.add_argument("start-maximized")  # https://stackoverflow.com/a/26283818/1689770
options.add_argument("enable-automation")  # https://stackoverflow.com/a/43840128/1689770
# options.add_argument("--headless")  # only if you are ACTUALLY running headless
options.add_argument("--no-sandbox")  # https://stackoverflow.com/a/50725918/1689770
options.add_argument("--disable-infobars")  # https://stackoverflow.com/a/43840128/1689770
options.add_argument("--disable-dev-shm-usage")  # https://stackoverflow.com/a/50725918/1689770
options.add_argument("--disable-browser-side-navigation")  # https://stackoverflow.com/a/49123152/1689770
options.add_argument("--disable-gpu")  # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc


def getData(url, driver):
    """
    Cette fonction prend en entr??e une url de data ainsi que le driver pour
    acqu??rir les donn??es des derniers port calls et les renvoyer sous la forme
    d'une liste.
    Exemple de liste r??duite renvoy?? :
    ['Ras Laffan, Qatar', 'Arrival (UTC)', 'Mar 22, 11:12', 'Departure (UTC)', 'Mar 23, 16:45', 'In Port', '1d 5h']
    """
    driver.get(url)
    try:
        # Liens vers les derniers ports visit??s
        Dwait(driver, 4).until(EC.presence_of_element_located((By.CLASS_NAME, "flx._rLk.t5UW5")))
    except TimeoutException:
        # Il n'y a pas les liens disponibles
        print(f"Timeout no port calls, url: {url}")
        try:
            # Premier cas : Aucun appel de ports d??tect??s
            Dwait(driver, 2).until(EC.presence_of_element_located((By.ID, "port-calls")))
        except Exception as e:
            # 2nd cas : il n'y a pas la section des derniers ports (bateaux peu utiles ?)
            print(f"error with {url} : {e}")
            list_pc = []
    finally:
        table = driver.find_elements_by_class_name('vfix-top')[3]
        list_pc = table.text.split('\n')
    return list_pc


def processData(list_pc, imo):
    """
    Cette fonction traite les donn??es de getData pour ??crire une seule string
    pr??te ?? ??tre copi?? dans le csv et qui contient toutes les lignes d'un bateau
    """
    str_pc = ''
    for i in range(len(list_pc)):
        if list_pc[i] == 'Arrival (UTC)':
            tab = list_pc[i-1].split(',')  # [Port, Country] (good) or [Port, Region, Country] (bad)
            if len(tab) == 3:
                tab = ['"' + tab[0] + ',' + tab[1].strip() + '"', tab[2]]  # [Port+(Region), Country]
            str_pc = str_pc + imo + ',' + tab[0] + ',' + tab[1] + ',"' + list_pc[i+1] + '","' + list_pc[i+3] + '","' + list_pc[i+5] + '"\n'
    return str_pc


def getAndWritePortCalls(name):
    """
    Cette fonction d??finit le driver (et ouvre la fen??tre chrome)
    et parcourt les lignes de data pour lancer l'acquisition sur une page
    Elle copie ensuite les donn??es trait??es dans le csv final
    """

    driver = webdriver.Chrome(options=options)

    # Permet d'avoir la taille pour utiliser la barre de chargement
    with open('../Data/data.csv') as f:
        boats_count = len(f.readlines())

    with open('../Data/data.csv', newline='') as csv_ship_infos:
        with open(f'../Data/Portcalls/{name}', 'a') as csv_pc:
            # Ecriture de l'en-t??te
            csv_pc.write('IMO,Port,Country,Arrival,Departure,In Port\n')
            # Barre de chargement dans le terminal
            bar = Bar('Processing', max=boats_count)
            ship_infos = csv.reader(csv_ship_infos)
            # On it??re sur tous les bateaux connus
            for row in ship_infos:
                if row[3] != 'Lien':
                    url = 'https://www.' + row[3]
                    imo = row[1]
                    list_data = getData(url, driver)
                    str_data = processData(list_data, imo)
                    csv_pc.write(str_data)
                    bar.next()
            bar.finish()


def convertPcDate(x):
    # On convertit les dates pour trier par mois puis jour
    if isinstance(x, str) and x != '-':
        try:
            # May 4, 21:16 -> 05/04, 21:16
            date = datetime.strptime(x, "%b %d, %H:%M").strftime("%m/%d, %H:%M")
        except ValueError:
            try:
                # La date est d??j?? au bon format
                date = datetime.strptime(x, "%m/%d, %H:%M").strftime("%m/%d, %H:%M")
            # Si rien ne marche, on renvoie '-' qui sera converti en nan
            except Exception:
                date = '-'
        except Exception:
            date = '-'
    else:
        date = '-'
    return date


def appendAndSelect(name):
    """
    Ajoute le fichier du jour au fichier commun en supprimant les doublons :
    1 . Les lignes qui sont toutes pareilles : Arrival, Departure, In Port
    2 . Les lignes ayant le m??me Arrival : on garde celle qui a le plus d'infos,
        notamment ayant les infos a, d, ip car certaines lignes correspondent
        ?? un bateau qui n'a pas encore quitt?? le port
    3 . Les lignes ayant le m??me Departure : on garde aussi celle qui a le plus d'infos,
        certaines dates de d??parts sont supprim??es quand elles sont trop anciennes
        (elles sont ici remplac??es par les dates de d??parts)

    pc = port calls
    """
    # On ajoute le nouveau fichier portcalls au fichier commun
    csv_pc = pd.read_csv(f'../Data/Portcalls/{name}', index_col=['IMO'])
    csv_all_pc = pd.read_csv('../Data/PortCalls/PortCalls.csv', index_col=['IMO'])
    csv_pc = csv_pc.append(csv_all_pc)
    size_before_add = csv_all_pc.shape[0]

    # On convertit les dates pour pouvoir trier le fichier
    csv_pc['Departure'] = csv_pc['Departure'].apply(convertPcDate)
    csv_pc['Arrival'] = csv_pc['Arrival'].apply(convertPcDate)

    # Gestion des nan + remplissage des dates d'arriv??es manquantes
    csv_pc = csv_pc.replace('-', np.nan)
    csv_pc['Arrival'].fillna(csv_pc['Departure'], inplace=True)

    # Etape 1
    csv_pc.drop_duplicates(inplace=True)
    # Etape 2
    csv_pc.sort_values(by=['IMO', 'Arrival'], na_position='first', inplace=True)
    csv_pc.drop_duplicates(subset=['Port', 'Country', 'Arrival'], keep='last', inplace=True)
    # Etape 3
    csv_pc.drop_duplicates(subset=['Port', 'Country', 'Departure'], keep='first', inplace=True)
    size_after_add = csv_pc.shape[0]

    # Ecriture dans le csv + communication dans le terminal
    csv_pc.to_csv('../Data/PortCalls/PortCalls.csv')
    print(f'{size_after_add - size_before_add} appels de ports ajout??s')


if __name__ == '__main__':
    today = date.today()
    name_file = f'PortCalls-{today}.csv'
    getAndWritePortCalls(name_file)
    appendAndSelect(name_file)
