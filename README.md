# ProjetInfo2021
Mines ParisTech - E-CUBE

Auteurs : Gabriel, Louis et Sophian



## Nomenclature des fichiers de code
Les fichiers de la phase de scraping commencent tous par la lettre A.
Les différents fichiers sont : 
* la liste des navires : `A11_list-vessels.py`
* le scraping journalier des informations sur chaque navire : `A12_scraping-vessels.py` (ainsi que le fichier de correction des dates `A121_scraping-vessels-corr.py`)
* les port calls : `A12_port-calls.py`
* les voyages réalisés par les navires : `A13_trips.py`
* les prix en Europe, Asie et Etats-Unis : `A2_Europe-futures.py`, `A2_Europe-spot.py`, `A2_Asia-futures.py`, `A2_USA-spot.py`

Il faut respecter l'ordre pour l'exécution : le fichier A12 a besoin du fichier A11 pour être exécuté (ou plus exactement du fichier créé par A11). Idem pour A13 avec A12.

Les fichiers de la phase de machine learning commencent tous par la lettre B.