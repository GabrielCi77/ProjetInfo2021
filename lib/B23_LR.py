import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
from B23_findCoeff import findBestCoeff2
import os


dict_area ={
    'EU' : 'Europe',
    'NA' : 'North America'
}
dict_reg = {
    'none': 'Regression linéaire',
    'l1' : 'Lasso',
    'l2' : 'Ridge'
    }
dict_reg_file = {
    'none': 'LR',
    'l1' : 'Lasso',
    'l2' : 'Ridge'
    }


def trainAndPlotAll(df_data, area = 'EU', penalty = 'none', shuffle = False, departures = False):
    """ Apprentissage par régression linéaire avec possibilité d'ajouter une régularisation (l1 ou l2)

    Paramètres
    ----------
    df_data : pandas.dataframe
        dictionnaire des paramètres
    area : string
        région d'arrivée étudiée (Europe, Amérique du Nord ou Asie)
        'EU' ou 'NA'
        par défaut : Europe
    penalty : string
        option d'ajout de régularisation
        'none', 'l1' ou 'l2'
        par défaut : pas de régularisation
    shuffle : boolean
        option pour la création des échantillons
    departures : boolean
        si True, on prend les départs comme variables

    Retours
    ----------
    Crée et enregistre les figures
    Affiche les performances
    """

    area_name = dict_area[area]
    penalty_name = dict_reg[penalty]
    penalty_filename = dict_reg_file[penalty]

    if not os.path.exists(f'../figure/A_prices/{area_name}_{penalty_filename}'):
        os.makedirs(f'../figure/A_prices/{area_name}_{penalty_filename}')
    
    # On ne garde que les jours où au moins 3 arrivées sont enregistrées
    df_data = df_data[(df_data['A_EU'] + df_data['A_NA'] + df_data['A_AS'] >= 3)]
    
    # On enlève les colonnes non utilisées pour le machine learning
    list_dates = np.array(df_data['Atime'])
    df_data = df_data.drop(columns=['Atime'])
    df_data = df_data.drop(
        columns=['Eur_Spot_12', 'Eur_Spot_9', 'Eur_Spot_6', 'Eur_Spot_3', 'Eur_Spot_0', 'Eur_Spot_-3', 'Eur_Spot_-6', 'Eur_Spot_-9', 'Eur_Spot_-12', 'Eur_Spot_-15', 'Eur_Spot_-18', 'Eur_Spot_-21',
        'US_Spot_12', 'US_Spot_9', 'US_Spot_6', 'US_Spot_3', 'US_Spot_0', 'US_Spot_-3', 'US_Spot_-6', 'US_Spot_-9', 'US_Spot_-12', 'US_Spot_-15', 'US_Spot_-18','US_Spot_-21',
        'Asia_Fut_12', 'Asia_Fut_9', 'Asia_Fut_6', 'Asia_Fut_3', 'Asia_Fut_0', 'Asia_Fut_-3', 'Asia_Fut_-6', 'Asia_Fut_-9', 'Asia_Fut_-12', 'Asia_Fut_-15', 'Asia_Fut_-18', 'Asia_Fut_-21']
        )

    if departures == True :
        pass
    else :
        df_data = df_data.drop(columns=['D_EU', 'D_AS', 'D_NA'])

    # On adapte au choix de la région
    if area == 'EU' :
        df_data = df_data.drop(columns=['A_AS', 'A_NA'])
        X = np.array(df_data.drop(columns=['A_EU']))
        y = np.array(df_data['A_EU'])
    elif area == 'NA' :
        df_data = df_data.drop(columns=['A_AS', 'A_EU'])
        X = np.array(df_data.drop(columns=['A_NA']))
        y = np.array(df_data['A_NA'])
    else :
        print("Area unvalid: choose between 'EU' (for Europe) and 'NA' (for North America)")
        return None

    # On crée les échantillons
    if shuffle :
        kf = KFold(n_splits=5, shuffle=True, random_state=13)
    else :
        kf = KFold(n_splits=5, shuffle=False)

    r2_scores = []
    rmse_scores = []

    # Boucle sur les différents échantillons
    for i, (train_index, test_index) in enumerate(kf.split(X)):
        print("fold: {0} | nb_train: {1} | nb_test: {2}".format(i, len(train_index), len(test_index)))

        # On sélectionne les jeux d'entraînement et de test
        X_train = X[train_index]
        X_test = X[test_index]
        y_train = y[train_index]
        y_test = y[test_index]

        list_dates_train = list_dates[train_index]
        list_dates_test = list_dates[test_index]

        # On applique un prétraitement aux données afin qu'elles soient centrées réduites
        standard_scaler = StandardScaler()
        standard_scaler.fit(X_train)
        X_train = standard_scaler.transform(X_train)
        X_test = standard_scaler.transform(X_test)
        
        # On sélectionne le modèle
        if penalty == 'l1' :
            best_alpha = findBestCoeff2(X, y, penalty)
            predictor = Lasso(alpha=best_alpha, random_state=13)
        elif penalty == 'l2' :
            best_alpha = findBestCoeff2(X, y, penalty)
            predictor = Ridge(alpha=best_alpha, random_state=13)
        else :
            predictor = LinearRegression()

        # On entraîne le modèle
        predictor.fit(X_train, y_train)
        # On réalise la prédiction sur le jeu de test
        y_pred = predictor.predict(X_test)

        # On mesure la performance
        r2_score_test = r2_score(y_test, y_pred)
        print("R2: {0:0.2f}".format(r2_score_test))
        r2_scores.append(r2_score_test)
        rmse_test = mean_squared_error(y_test, y_pred, squared=False)
        print("RMSE : {0:0.2f}".format(rmse_test))
        rmse_scores.append(rmse_test)

        # On regarde les coefficients des différentes variables
        num_features = X_train.shape[1]
        feature_names = df_data.drop(columns=['A_EU']).columns
        plt.scatter(range(num_features), np.abs(predictor.coef_))
        plt.xlabel('Variables')
        tmp = plt.xticks(range(num_features), feature_names, rotation=90)
        tmp = plt.ylabel('Coefficients')
        plt.title(f'Coefficients avec {penalty_name}')
        plt.savefig(f'../figure/A_prices/{area_name}_{penalty_filename}/B3_noD_{penalty_filename}_coeff_{i}.png')
        plt.show()

        # On compare les prédictions aux valeurs réelles
        fig = plt.figure(figsize=(5, 5))
        plt.scatter(y_test, y_pred)
        plt.xlabel("Nombre réel")
        plt.ylabel("Nombre prédit")
        plt.title(f'{penalty_name} : nombre de navires arrivant en Europe (RMSE = {mean_squared_error(y_test, y_pred, squared=False)})')
        axis_min = np.min([np.min(y_test), np.min(y_pred)])-1 # Mêmes valeurs sur les deux axes
        axis_max = np.max([np.max(y_test), np.max(y_pred)])+1
        plt.xlim(axis_min, axis_max)
        plt.ylim(axis_min, axis_max)
        plt.plot([axis_min, axis_max], [axis_min, axis_max], 'k-') # Diagonale y=x
        plt.savefig(f'../figure/A_prices/{area_name}_{penalty_filename}/B3_noD_{penalty_filename}_diag_{i}.png')
        plt.show()

        # On regarde l'évolution temporelle
        plt.plot(list_dates, y, 'b')
        plt.plot(list_dates_test, y_pred, 'r')
        plt.xlabel("Temps")
        plt.ylabel("Nombre de navires arrivant en Europe")
        plt.legend(('Evolution réelle', f'Evolution prédite ({penalty_name})'), loc='upper right')
        plt.title("RMSE : %.2f" % mean_squared_error(y_test, y_pred, squared=False))
        plt.savefig(f'../figure/A_prices/{area_name}_{penalty_filename}/B3_noD_{penalty_filename}_vesselsperday_{i}.png')
        plt.show()


    print()
    
    # performance on the test set
    average_r2_score = np.mean(r2_scores)
    std_r2_score = np.std(r2_scores)
    print("Average R2: {0:0.3f}".format(average_r2_score))
    print("Standard deviation R2: {0:0.3f}".format(std_r2_score))
    average_rmse_score = np.mean(rmse_scores)
    std_rmse_score = np.std(rmse_scores)
    print("Average RMSE: {0:0.3f}".format(average_rmse_score))
    print("Standard deviation RMSE: {0:0.3f}".format(std_rmse_score))


if __name__ == '__main__':
    df_trips = pd.read_csv('../data/loadAll_extended_A_agg_All.csv')
    trainAndPlotAll(df_trips, 'EU', 'l2', False, False)