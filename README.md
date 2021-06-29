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
Les différents fichiers sont :
* B11 : premiers formatages de données : `B11_Create_df.py`
* B12 : formatages finaux : `B12_df_creation.py`, `B12_sum.py`

* B21 : premiers essais de machine learning (classification) : `B21_first.py`, `B21_LR_discrete.py`, `B21_ML_LR.py`, `B21_ML_NN.py`, , `B21_ML_test.py`
first, ML_, LR_discrete
* B23 : versions finales : `B23_Arima.py`, `B23_LR.py`, `B23_findCoeff.py`