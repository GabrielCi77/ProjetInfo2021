import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_validate, GridSearchCV
from sklearn.linear_model import LinearRegression as LR
from sklearn import preprocessing
from sklearn import metrics
from datetime import datetime, timedelta
import matplotlib.pyplot as plt



def trainAndPlotAll(df_data):
    # On ne garde que les jours où au moins 3 arrivées sont enregistrées
    df_data = df_data[(df_data['A_EU'] + df_data['A_NA'] + df_data['A_AS'] >= 3)]
    
    # On enlève les colonnes non utilisées pour le machine learning
    list_dates = np.array(df_data['Atime'])
    df_data = df_data.drop(columns=['Atime', 'A_AS', 'A_NA'])

    X = np.array(df_data.drop(columns=['A_EU']))
    y = np.array(df_data['A_EU'])

    kf = KFold(n_splits=5, shuffle=True, random_state=13)

    scores = []

    # loop over the different folds
    for i, (train_index, test_index) in enumerate(kf.split(X)):
        print("fold: {0} | nb_train: {1} | nb_test: {2}".format(i, len(train_index), len(test_index)))

        # get train and validation dataset
        X_train = X[train_index]
        X_test = X[test_index]
        y_train = y[train_index]
        y_test = y[test_index]

        list_dates_train = list_dates[train_index]
        list_dates_test = list_dates[test_index]
        
        # train model
        predictor = LR()
        predictor.fit(X_train, y_train)
        
        # measure performance
        y_pred = predictor.predict(X_test)
        print("RMSE: %.2f" % metrics.mean_squared_error(y_test, y_pred, squared=False))
        scores.append(metrics.mean_squared_error(y_test, y_pred, squared=False))

        # On regarde les coefficients des différentes variables
        num_features = X_train.shape[1]
        feature_names = df_data.drop(columns=['A_EU']).columns
        plt.scatter(range(num_features), np.abs(predictor.coef_))
        plt.xlabel('Variables')
        tmp = plt.xticks(range(num_features), feature_names, rotation=90)
        tmp = plt.ylabel('Coefficients')
        plt.title("Coefficients de la régression linéaire")
        plt.savefig(f'../figure/B22_LR_time_coeff_{i}.png')
        plt.show()

        # On compare les prédictions aux valeurs réelles
        fig = plt.figure(figsize=(5, 5))
        plt.scatter(y_test, y_pred)

        plt.xlabel("Nombre réel")
        plt.ylabel("Nombre prédit")
        plt.title(f'Régression linéaire : nombre de navires arrivant en Europe (RMSE = {metrics.mean_squared_error(y_test, y_pred, squared=False)})')

        # Mêmes valeurs sur les deux axes
        axis_min = np.min([np.min(y_test), np.min(y_pred)])-1
        axis_max = np.max([np.max(y_test), np.max(y_pred)])+1
        plt.xlim(axis_min, axis_max)
        plt.ylim(axis_min, axis_max)
        
        # Diagonale y=x
        plt.plot([axis_min, axis_max], [axis_min, axis_max], 'k-')
        plt.savefig(f'../figure/B22_LR_time_diag_{i}.png')
        plt.show()


        # Evolution temporelle
        plt.plot(list_dates, y, 'b')
        plt.plot(list_dates_test, y_pred, 'r')
        plt.xlabel("Temps")
        plt.ylabel("Nombre de navires arrivant en Europe")
        plt.legend(('Evolution réelle', 'Evolution prédite'), loc='upper right')
        plt.title("RMSE : %.2f" % metrics.mean_squared_error(y_test, y_pred, squared=False))
        plt.savefig(f'../figure/B22_LR_time_vesselsperday_{i}.png')
        plt.show()

    print(scores)

    # performance on the test set
    average_score = np.mean(scores)
    std_score = np.std(scores)
    print("Average RMSE (test): {0:0.3f}".format(average_score))
    print("Standard deviation RMSE (test): {0:0.3f}".format(std_score), "\n")


if __name__ == '__main__':
    df_trips = pd.read_csv('../data/loadAll_agg_all.csv')
    trainAndPlotAll(df_trips)