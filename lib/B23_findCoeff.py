import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Lasso, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt



# Fonction qu'on peut tester (toute seule) avec ce fichier

def findBestCoeff(df_data, model, print_results=False):
    """ Trouve le meilleur coefficient pour le lasso

    Paramètres
    ----------
    df_data : pandas.dataframe
        dictionnaire des paramètres
    model : string
        'l1' ou 'l2'
        choix du modèle (Lasso ou Ridge)

    Retours
    ----------
    alpha : float
        meilleur coefficient dans la liste proposée
    """
    
    # On ne garde que les jours où au moins 3 arrivées sont enregistrées
    df_data = df_data[(df_data['A_EU'] + df_data['A_NA'] + df_data['A_AS'] >= 3)]
    
    # On enlève les colonnes non utilisées pour le machine learning
    list_dates = np.array(df_data['Atime'])
    df_data = df_data.drop(columns=['Atime', 'A_AS', 'A_NA'])

    X = np.array(df_data.drop(columns=['A_EU']))
    y = np.array(df_data['A_EU'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=13)

    # On applique un prétraitement aux données afin qu'elles soient centrées réduites
    standard_scaler = StandardScaler()
    standard_scaler.fit(X_train)
    X_train = standard_scaler.transform(X_train)
    X_test = standard_scaler.transform(X_test)
        
    # define model and alpha values to evaluate
    if model == 'l1' :
        predictor = Lasso(random_state=13, max_iter=10000)
    elif model == 'l2' :
        predictor = Ridge(random_state=13, max_iter=10000)
    else :
        print("Model unvalid: choose between 'l1' (for Lasso) and 'l2' (for Ridge)")
        return None
    
    alphas = np.logspace(-4, 0, 30)

    # define gridsearch
    tuned_parameters = [{'alpha': alphas}]
    nb_folds = 5
    grid = GridSearchCV(predictor, tuned_parameters, cv=nb_folds, refit=False, verbose=3)

    # run gridsearch 
    grid.fit(X_train, y_train)

    # get R2 (default score with Lasso models)
    scores = grid.cv_results_['mean_test_score']
    scores_std = grid.cv_results_['std_test_score']

    # compute standard errors
    std_error = scores_std / np.sqrt(nb_folds)

    # get optimal alpha
    i_max = np.argmax(scores)
    best_alpha = alphas[i_max]
    best_score = scores[i_max]
    if print_results :
        print("optimal alpha: {0:0.4f}".format(best_alpha))
        print("best R2 (test set): {0:0.4f}".format(best_score))

    return best_alpha



# Fonction utilisée dans B23_LR.property

def findBestCoeff2(X, y, model):
    """ Trouve le meilleur coefficient pour le lasso

    Paramètres
    ----------
    X : 
    y : 
    model : string
        'l1' ou 'l2'
        choix du modèle (Lasso ou Ridge)

    Retours
    ----------
    alpha : float
        meilleur coefficient dans la liste proposée
    """

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=13)

    # On applique un prétraitement aux données afin qu'elles soient centrées réduites
    standard_scaler = StandardScaler()
    standard_scaler.fit(X_train)
    X_train = standard_scaler.transform(X_train)
    X_test = standard_scaler.transform(X_test)
        
    # define model and alpha values to evaluate
    if model == 'l1' :
        predictor = Lasso(random_state=13, max_iter=10000)
    elif model == 'l2' :
        predictor = Ridge(random_state=13, max_iter=10000)
    else :
        print("Model unvalid: choose between 'l1' (for Lasso) and 'l2' (for Ridge)")
        return None
    
    alphas = np.logspace(-4, 0, 30)

    # define gridsearch
    tuned_parameters = [{'alpha': alphas}]
    nb_folds = 5
    grid = GridSearchCV(predictor, tuned_parameters, cv=nb_folds, refit=False, verbose=0)

    # run gridsearch 
    grid.fit(X_train, y_train)

    # get R2 (default score with Lasso models)
    scores = grid.cv_results_['mean_test_score']
    scores_std = grid.cv_results_['std_test_score']

    # compute standard errors
    std_error = scores_std / np.sqrt(nb_folds)

    # get optimal alpha
    i_max = np.argmax(scores)
    best_alpha = alphas[i_max]
    # best_score = scores[i_max]

    return best_alpha



if __name__ == '__main__':
    df_trips = pd.read_csv('../data/loadAll_agg_all.csv')
    alpha = findBestLassoCoeff(df_trips, 'l1', True)
