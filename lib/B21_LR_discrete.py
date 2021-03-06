import numpy as np
import pandas as pd
from sklearn import model_selection
from sklearn.linear_model import LinearRegression as LR
from sklearn import preprocessing
from sklearn import metrics
from datetime import datetime, timedelta
import matplotlib.pyplot as plt



def trainAndPlotAll(df_data):
    # On ne garde que ceux qui arrivent en Europe, en Amérique du Nord ou en Asie
    df_data = df_data[(df_data['A_EU'] + df_data['A_NA'] + df_data['A_AS'] == 1)]
    
    # On enlève les colonnes non utilisées pour le machine learning
    df_data = df_data.drop(columns=['IMO', 'Dport', 'Dcountry', 'Aport', 'Acountry'])
    df_data = df_data.drop(columns=['Dtime', 'Atime', 'D_SA', 'A_SA', 'D_AF', 'A_AF', 'D_OC', 'A_OC', 'A_NA', 'A_AS'])

    X = np.array(df_data.drop(columns=['A_EU']))
    y = np.array(df_data['A_EU'])

    # On sépare en deux jeux de données
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, 
                                                                    test_size=0.20, 
                                                                    random_state=27)

    standard_scaler = preprocessing.StandardScaler()
    standard_scaler.fit(X_train)
    X_train = standard_scaler.transform(X_train)
    X_test = standard_scaler.transform(X_test)

    # On entraine une régression linéaire
    print(len(X_train), len(y_train))
    predictor = LR()
    predictor.fit(X_train, y_train)

    # On la teste sur le jeu de test
    y_pred = predictor.predict(X_test)
    print("RMSE: %.2f" % metrics.mean_squared_error(y_test, y_pred, squared=False))

    # On regarde les coefficients des différentes variables
    num_features = X_train.shape[1]
    feature_names = df_data.drop(columns=['A_EU']).columns
    plt.scatter(range(num_features), np.abs(predictor.coef_))
    plt.xlabel('Variables')
    tmp = plt.xticks(range(num_features), feature_names, rotation=90)
    tmp = plt.ylabel('Coefficient')
    plt.show()

    # fig = plt.figure(figsize=(5, 5))
    # plt.scatter(y_test, y_pred)

    # # plt.xlabel("Consommation réelle (mpg)")
    # # plt.ylabel("Consommation prédite (mpg)")
    # plt.title("Régression linéaire")

    # # Mêmes valeurs sur les deux axes
    # axis_min = np.min([np.min(y_test), np.min(y_pred)])-1
    # axis_max = np.max([np.max(y_test), np.max(y_pred)])+1
    # plt.xlim(axis_min, axis_max)
    # plt.ylim(axis_min, axis_max)
    
    # # Diagonale y=x
    # plt.plot([axis_min, axis_max], [axis_min, axis_max], 'k-')
    # plt.show()


if __name__ == '__main__':
    df_trips = pd.read_csv('../data/loadAll.csv')

    # On enlève les lignes avec des cases vides
    df_trips = df_trips.dropna(axis = 0, how = 'any', inplace = False)

    trainAndPlotAll(df_trips)